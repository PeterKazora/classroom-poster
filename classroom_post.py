"""Post to Google Classroom from the command line.

One-time setup: see SETUP.md (credentials.json must sit next to this file).

Examples
  python classroom_post.py courses
  python classroom_post.py topics  --course "9C"
  python classroom_post.py post    --course "9C" --topic "MATHS VIDEOS" \
        --title "Algebra notes" --desc-file desc.txt \
        --file "C:/path/notes.pdf" --link https://example.com --draft
  python classroom_post.py list    --course "9C"
  python classroom_post.py delete  --course "9C" --id 123456789
  python classroom_post.py courses --account home

--course matches any part of the class name (case-insensitive) and can be
given more than once to post the same thing to several classes.
"""

import argparse
import datetime as dt
import mimetypes
import os
import re
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

HERE = os.path.dirname(os.path.abspath(__file__))
DRIVE_FOLDER = "Classroom Poster uploads"

# --account picks which Google account (and which key/login files) to use:
# "default" uses credentials.json + token.json, any other NAME uses
# credentials-NAME.json + token-NAME.json.
CREDENTIALS = TOKEN = ACCOUNT = None


def use_account(name):
    global CREDENTIALS, TOKEN, ACCOUNT
    if not re.fullmatch(r"[\w-]+", name):
        sys.exit("--account names may only use letters, digits, - and _.")
    suffix = "" if name == "default" else f"-{name}"
    ACCOUNT = name
    CREDENTIALS = os.path.join(HERE, f"credentials{suffix}.json")
    TOKEN = os.path.join(HERE, f"token{suffix}.json")

SCOPES = [
    "https://www.googleapis.com/auth/classroom.courses.readonly",
    "https://www.googleapis.com/auth/classroom.topics",
    "https://www.googleapis.com/auth/classroom.courseworkmaterials",
    "https://www.googleapis.com/auth/classroom.announcements",
    "https://www.googleapis.com/auth/classroom.coursework.students",
    "https://www.googleapis.com/auth/drive.file",
]


# ---------- auth ----------

def get_creds():
    creds = None
    if os.path.exists(TOKEN):
        creds = Credentials.from_authorized_user_file(TOKEN, SCOPES)
    if creds and creds.valid:
        return creds
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None
    if not creds or not creds.valid:
        if not os.path.exists(CREDENTIALS):
            sys.exit(f"Missing {CREDENTIALS}. Follow SETUP.md first.")
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
        print(f'A browser window will open. Sign in with your "{ACCOUNT}" Google account and click Allow.')
        creds = flow.run_local_server(port=0)
    with open(TOKEN, "w", encoding="utf-8") as f:
        f.write(creds.to_json())
    return creds


def services():
    creds = get_creds()
    return (build("classroom", "v1", credentials=creds, cache_discovery=False),
            build("drive", "v3", credentials=creds, cache_discovery=False))


# ---------- lookups ----------

def all_courses(cls):
    out, token = [], None
    while True:
        r = cls.courses().list(teacherId="me", courseStates=["ACTIVE"],
                               pageSize=100, pageToken=token).execute()
        out += r.get("courses", [])
        token = r.get("nextPageToken")
        if not token:
            return out


def find_course(cls, query):
    courses = all_courses(cls)
    q = query.lower()
    exact = [c for c in courses if c["name"].lower() == q or c["id"] == query]
    hits = exact or [c for c in courses
                     if q in f'{c["name"]} {c.get("section", "")}'.lower()]
    if len(hits) == 1:
        return hits[0]
    if not hits:
        sys.exit(f'No active class matches "{query}". Run: python classroom_post.py courses')
    names = "\n  ".join(f'{c["name"]}  ({c["id"]})' for c in hits)
    sys.exit(f'"{query}" matches several classes - be more specific:\n  {names}')


def all_topics(cls, course_id):
    out, token = [], None
    while True:
        r = cls.courses().topics().list(courseId=course_id, pageSize=100,
                                        pageToken=token).execute()
        out += r.get("topic", [])
        token = r.get("nextPageToken")
        if not token:
            return out


def find_or_create_topic(cls, course_id, query, create):
    topics = all_topics(cls, course_id)
    q = query.lower()
    exact = [t for t in topics if t["name"].lower() == q]
    hits = exact or [t for t in topics if q in t["name"].lower()]
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        names = ", ".join(f'"{t["name"]}"' for t in hits)
        sys.exit(f'Topic "{query}" is ambiguous: {names}')
    if not create:
        sys.exit(f'No topic matches "{query}". Add --new-topic to create it.')
    print(f'  creating topic "{query}"')
    return cls.courses().topics().create(courseId=course_id, body={"name": query}).execute()


# ---------- drive ----------

def upload_folder(drive):
    q = (f"name = '{DRIVE_FOLDER}' and mimeType = 'application/vnd.google-apps.folder' "
         "and trashed = false")
    found = drive.files().list(q=q, fields="files(id)").execute().get("files", [])
    if found:
        return found[0]["id"]
    return drive.files().create(body={"name": DRIVE_FOLDER,
                                      "mimeType": "application/vnd.google-apps.folder"},
                                fields="id").execute()["id"]


def upload(drive, path, folder_id):
    if not os.path.isfile(path):
        sys.exit(f"File not found: {path}")
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    print(f"  uploading {os.path.basename(path)} ...")
    media = MediaFileUpload(path, mimetype=mime, resumable=True)
    f = drive.files().create(body={"name": os.path.basename(path), "parents": [folder_id]},
                             media_body=media, fields="id").execute()
    return f["id"]


# ---------- building the post ----------

def youtube_id(url):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([\w-]{11})", url)
    if not m:
        sys.exit(f"Not a YouTube link: {url}")
    return m.group(1)


def parse_when(text):
    """'2026-10-20 07:00' in local time -> RFC3339 UTC string."""
    local = dt.datetime.strptime(text, "%Y-%m-%d %H:%M").astimezone()
    return local.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), local


def materials_from(args, drive_ids):
    mats = [{"driveFile": {"driveFile": {"id": i}, "shareMode": "VIEW"}} for i in drive_ids]
    mats += [{"link": {"url": u}} for u in args.link]
    mats += [{"youtubeVideo": {"id": youtube_id(u)}} for u in args.youtube]
    if len(mats) > 20:
        sys.exit("Classroom allows at most 20 attachments per post. Put extra links in the description.")
    return mats


def cmd_post(args):
    desc = args.desc or ""
    if args.desc_file:
        with open(args.desc_file, encoding="utf-8") as f:
            desc = f.read().strip()
    if args.kind != "announcement" and not args.title:
        sys.exit("--title is required for materials and assignments.")
    if args.kind == "announcement" and not desc:
        sys.exit("Announcements need --desc or --desc-file (that is the announcement text).")
    when = parse_when(args.schedule) if args.schedule else None

    print("\n=== POST PREVIEW ===")
    print(f"Account:  {ACCOUNT}")
    print(f"Type:     {args.kind}")
    print(f"Classes:  {', '.join(args.course)}")
    if args.kind != "announcement":
        print(f"Topic:    {args.topic or '(no topic)'}")
        print(f"Title:    {args.title}")
    print(f"State:    {'scheduled for ' + when[1].strftime('%a %d %b %H:%M') if when else 'DRAFT (only you see it)' if args.draft else 'PUBLISHED now - students are notified'}")
    if args.due:
        print(f"Due:      {args.due}")
    print(f"Files:    {', '.join(os.path.basename(p) for p in args.file) or '-'}")
    print(f"Links:    {len(args.link)}   YouTube: {len(args.youtube)}")
    print("Text:\n  " + (desc.replace("\n", "\n  ") if desc else "-"))
    print("====================\n")
    if args.dry_run:
        print("Dry run - nothing posted.")
        return

    cls, drive = services()
    drive_ids = []
    if args.file:
        folder = upload_folder(drive)
        drive_ids = [upload(drive, p, folder) for p in args.file]
    mats = materials_from(args, drive_ids)

    for cq in args.course:
        course = find_course(cls, cq)
        cid = course["id"]
        body = {"materials": mats} if mats else {}
        if when:
            body.update(state="DRAFT", scheduledTime=when[0])
        else:
            body["state"] = "DRAFT" if args.draft else "PUBLISHED"
        try:
            if args.kind == "announcement":
                body["text"] = desc
                res = cls.courses().announcements().create(courseId=cid, body=body).execute()
            else:
                body["title"] = args.title
                if desc:
                    body["description"] = desc
                if args.topic:
                    body["topicId"] = find_or_create_topic(cls, cid, args.topic, args.new_topic)["topicId"]
                if args.kind == "material":
                    res = cls.courses().courseWorkMaterials().create(courseId=cid, body=body).execute()
                else:
                    body["workType"] = "ASSIGNMENT"
                    if args.points is not None:
                        body["maxPoints"] = args.points
                    if args.due:
                        due_utc = dt.datetime.strptime(args.due, "%Y-%m-%d %H:%M").astimezone().astimezone(dt.timezone.utc)
                        body["dueDate"] = {"year": due_utc.year, "month": due_utc.month, "day": due_utc.day}
                        body["dueTime"] = {"hours": due_utc.hour, "minutes": due_utc.minute}
                    res = cls.courses().courseWork().create(courseId=cid, body=body).execute()
        except HttpError as e:
            sys.exit(f'Google refused the post to "{course["name"]}": {e.reason if hasattr(e, "reason") else e}')
        print(f'Posted to {course["name"]}: {res.get("alternateLink", res.get("id"))}  [id {res["id"]}]')


def cmd_courses(args):
    cls, _ = services()
    for c in sorted(all_courses(cls), key=lambda c: c["name"].lower()):
        sec = f' - {c["section"]}' if c.get("section") else ""
        print(f'{c["name"]}{sec}   (id {c["id"]})')


def cmd_topics(args):
    cls, _ = services()
    course = find_course(cls, args.course[0])
    print(f'Topics in {course["name"]}:')
    for t in all_topics(cls, course["id"]):
        print(f'  {t["name"]}')


def cmd_list(args):
    cls, _ = services()
    course = find_course(cls, args.course[0])
    cid = course["id"]
    topics = {t["topicId"]: t["name"] for t in all_topics(cls, cid)}
    rows = []
    for kind, call, key in (
        ("material", cls.courses().courseWorkMaterials().list, "courseWorkMaterial"),
        ("assignment", cls.courses().courseWork().list, "courseWork"),
        ("announcement", cls.courses().announcements().list, "announcements"),
    ):
        for it in call(courseId=cid, pageSize=30).execute().get(key, []):
            title = it.get("title") or it.get("text", "")[:50].replace("\n", " ")
            rows.append((it.get("creationTime", ""), kind, it["state"], title,
                         topics.get(it.get("topicId"), ""), it["id"]))
    print(f'Latest posts in {course["name"]} (newest first):')
    for created, kind, state, title, topic, pid in sorted(rows, reverse=True)[:args.limit]:
        print(f'  {created[:16].replace("T", " ")}  {kind:<12} {state:<9} {title}  [{topic}]  id {pid}')


def cmd_edit(args):
    desc = args.desc
    if args.desc_file:
        with open(args.desc_file, encoding="utf-8") as f:
            desc = f.read().strip()
    if desc is None and args.title is None:
        sys.exit("Give --title and/or --desc / --desc-file to change.")
    cls, _ = services()
    course = find_course(cls, args.course[0])
    cid = course["id"]
    for kind, api, desc_field in (("material", cls.courses().courseWorkMaterials(), "description"),
                                  ("assignment", cls.courses().courseWork(), "description"),
                                  ("announcement", cls.courses().announcements(), "text")):
        try:
            item = api.get(courseId=cid, id=args.id).execute()
        except HttpError:
            continue
        body, mask = {}, []
        if desc is not None:
            body[desc_field] = desc
            mask.append(desc_field)
        if args.title is not None and kind != "announcement":
            body["title"] = args.title
            mask.append("title")
        print(f'Editing {kind} "{item.get("title") or item.get("text", "")[:60]}" in {course["name"]}')
        if desc is not None:
            print("New text:\n  " + desc.replace("\n", "\n  "))
        if args.dry_run:
            print("Dry run - nothing changed.")
            return
        try:
            api.patch(courseId=cid, id=args.id, updateMask=",".join(mask), body=body).execute()
        except HttpError as e:
            sys.exit(f"Google refused: {e}\n(Posts made by hand on the website can only be edited on the website.)")
        print("Saved. (Editing does not notify students.)")
        return
    sys.exit(f"No post with id {args.id} in {course['name']}.")


def cmd_delete(args):
    cls, _ = services()
    course = find_course(cls, args.course[0])
    cid = course["id"]
    for kind, api in (("material", cls.courses().courseWorkMaterials()),
                      ("assignment", cls.courses().courseWork()),
                      ("announcement", cls.courses().announcements())):
        try:
            item = api.get(courseId=cid, id=args.id).execute()
        except HttpError:
            continue
        title = item.get("title") or item.get("text", "")[:60]
        if not args.yes:
            ans = input(f'Delete {kind} "{title}" from {course["name"]}? Type yes: ')
            if ans.strip().lower() != "yes":
                sys.exit("Cancelled.")
        try:
            api.delete(courseId=cid, id=args.id).execute()
        except HttpError as e:
            sys.exit(f"Google refused: {e}\n(Posts made by hand on the website can only be deleted on the website.)")
        print(f'Deleted {kind} "{title}".')
        return
    sys.exit(f"No post with id {args.id} in {course['name']}.")


def main():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--account", default="default",
                        help="which Google account to use, see SETUP.md (default: default)")
    p = argparse.ArgumentParser(description="Post to Google Classroom.")
    sub = p.add_subparsers(dest="cmd", required=True)
    _add = sub.add_parser
    sub.add_parser = lambda *a, **k: _add(*a, parents=[common], **k)

    sub.add_parser("courses", help="list your active classes")

    t = sub.add_parser("topics", help="list topics in a class")
    t.add_argument("--course", action="append", required=True)

    l = sub.add_parser("list", help="list recent posts in a class (with ids)")
    l.add_argument("--course", action="append", required=True)
    l.add_argument("--limit", type=int, default=20)

    e = sub.add_parser("edit", help="change the title/description of a post made by this program")
    e.add_argument("--course", action="append", required=True)
    e.add_argument("--id", required=True)
    e.add_argument("--title")
    e.add_argument("--desc")
    e.add_argument("--desc-file")
    e.add_argument("--dry-run", action="store_true")

    d = sub.add_parser("delete", help="delete a post made by this program")
    d.add_argument("--course", action="append", required=True)
    d.add_argument("--id", required=True)
    d.add_argument("--yes", action="store_true", help="skip the confirmation question")

    s = sub.add_parser("post", help="create a material, announcement or assignment")
    s.add_argument("--course", action="append", required=True, help="class name (repeat for several classes)")
    s.add_argument("--kind", choices=["material", "announcement", "assignment"], default="material")
    s.add_argument("--title")
    s.add_argument("--desc", help="description text")
    s.add_argument("--desc-file", help="UTF-8 text file holding the description")
    s.add_argument("--topic", help="topic name (part of the name is enough)")
    s.add_argument("--new-topic", action="store_true", help="create the topic if it does not exist")
    s.add_argument("--file", action="append", default=[], help="local file to upload and attach (repeatable)")
    s.add_argument("--link", action="append", default=[], help="web link to attach (repeatable)")
    s.add_argument("--youtube", action="append", default=[], help="YouTube video to attach (repeatable)")
    s.add_argument("--draft", action="store_true", help="save as draft instead of publishing")
    s.add_argument("--schedule", help='publish later, local time "YYYY-MM-DD HH:MM"')
    s.add_argument("--due", help='assignment due time, local "YYYY-MM-DD HH:MM"')
    s.add_argument("--points", type=int, help="assignment max points")
    s.add_argument("--dry-run", action="store_true", help="show the preview only, post nothing")

    args = p.parse_args()
    use_account(args.account)
    {"courses": cmd_courses, "topics": cmd_topics, "list": cmd_list,
     "delete": cmd_delete, "post": cmd_post, "edit": cmd_edit}[args.cmd](args)


if __name__ == "__main__":
    main()
