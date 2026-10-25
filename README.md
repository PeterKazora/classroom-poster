# Classroom Poster

Post to Google Classroom from the command line: notes, links, YouTube videos and local
files, to one class or several at once, now or at a set time.

I teach several classes and kept posting the same revision guide to each one by hand:
upload the file, attach it, pick the topic, type the text, then do it all again for the
next class. This tool does that in one command, and shows exactly what it will post
before anything reaches students.

## What it does

- **Materials, announcements and assignments** (with due date and points)
- **Several classes in one go**: give `--course` more than once
- **Local files are uploaded to Drive** and attached for you (into a Drive folder called
  *Classroom Poster uploads*)
- **Links and YouTube videos** attached as proper Classroom attachments
- **Topics**: post into an existing topic, or create it with `--new-topic`
- **Drafts and scheduling**: `--draft` to check it in Classroom first, `--schedule` to
  publish later
- **Preview first**: every post prints a preview; `--dry-run` stops there and posts nothing
- **List, edit and delete** posts the tool made
- **Two Google accounts** (say school and personal) with `--account`
- Class and topic names match on any part of the name, so `--course "9C"` finds
  *Mathematics 9C*

## Quick start

1. Install the libraries (Python 3.9+):

   ```bash
   pip install -r requirements.txt
   ```

2. Follow [SETUP.md](SETUP.md) once (about 15 minutes) to create your own free Google
   Cloud app and download its key file, `credentials.json`.
3. List your classes (the first run opens a browser to sign in):

   ```bash
   python classroom_post.py courses
   ```

## Examples

Post notes to two classes, into the *Revision* topic, scheduled for Tuesday morning:

```bash
python classroom_post.py post --course "Year 10" --course "Year 11" --topic "Revision" --title "Unit 3 revision guide" --desc-file desc.txt --file unit3-guide.pdf --youtube https://youtu.be/VIDEO_ID --schedule "2026-10-27 07:00"
```

Every post starts with a preview like this:

```text
=== POST PREVIEW ===
Account:  default
Type:     material
Classes:  Year 10, Year 11
Topic:    Revision
Title:    Unit 3 revision guide
State:    scheduled for Tue 27 Oct 07:00
Files:    unit3-guide.pdf
Links:    0   YouTube: 1
Text:
  Revision guide for Unit 3. Read pages 1-4 before Monday.
  Quiz on Friday.
====================
```

More:

```bash
python classroom_post.py post --course "9C" --kind announcement --desc "No homework this week."
python classroom_post.py post --course "9C" --kind assignment --title "Algebra worksheet" --file algebra.pdf --due "2026-10-30 17:00" --points 20
python classroom_post.py post --course "9C" --title "Algebra notes" --file notes.pdf --dry-run
python classroom_post.py topics --course "9C"
python classroom_post.py list   --course "9C"
python classroom_post.py edit   --course "9C" --id 123456789 --desc-file new-text.txt
python classroom_post.py delete --course "9C" --id 123456789
```

Run `python classroom_post.py post --help` for every option.

## Good to know

- **Students are notified** when a post is published. Use `--draft` or `--dry-run`
  until you trust a command.
- Google only lets the tool **edit or delete posts it made**. Posts made by hand on the
  website have to be changed there.
- At most **20 attachments** per post (Google's limit).
- Editing a post does not notify students.

## Privacy

The tool talks only to Google, using an app you create in your own Google account. No
other server is involved. Your key and sign-in files (`credentials*.json`,
`token*.json`) stay on your computer and are listed in `.gitignore`, so they are never
uploaded to GitHub. To revoke access, remove *Classroom Poster* at
https://myaccount.google.com/permissions.

## Extras

`extras/make_banner.py` draws a 2000 × 500 header image for a physics class (seven
topic panels of formulas and diagrams). Edit `PANELS` for your own subject. Needs
`numpy` and `matplotlib`.

## Licence

MIT: free to use, change and share. See [LICENSE](LICENSE).

Built with [Claude Code](https://claude.com/claude-code) by a Cambridge maths and
physics teacher in Kampala, Uganda. Issues and pull requests are welcome.
