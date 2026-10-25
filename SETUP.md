# Classroom Poster – one-time setup (about 15 minutes)

Google only lets a program post to your classes if you create a small "app" for it in
your own Google account. You do this once. Nothing here costs money.

Do every step signed in as the Google account you **teach with** (the one that owns
your classes). Tip: use a browser window that is signed in only to that account, or
check the account picture at the top right of each page.

---

## Step 0 – Install Python and the libraries

1. Install Python 3.9 or newer from https://www.python.org (on Windows, tick
   *Add Python to PATH*).
2. In a terminal, in this folder, run:

   ```
   pip install -r requirements.txt
   ```

## Step 1 – Create a Google Cloud project

1. Go to **https://console.cloud.google.com**
2. If asked, agree to the Terms of Service.
3. Click the project picker at the top (it may say *Select a project*) → **New project**.
4. Name: `Classroom Poster` → **Create**. Wait a few seconds, then make sure the
   new project is selected in the picker.

> **If you see "You don't have permission to create a project"**, your school's IT
> has switched this off. Ask them to allow it, or use a personal Google account
> for your classes instead.

## Step 2 – Switch on the two APIs

Open each link, check the project at the top is *Classroom Poster*, and click
**Enable**. Wait until the button changes to **Manage**.

- https://console.cloud.google.com/apis/library/classroom.googleapis.com
- https://console.cloud.google.com/apis/library/drive.googleapis.com

## Step 3 – Consent screen (tells Google this app is yours)

1. Open **https://console.cloud.google.com/auth/overview** (it may be called
   *OAuth consent screen* or *Google Auth Platform*) → **Get started**.
2. App name: `Classroom Poster`. User support email: your email → **Next**.
3. Audience:
   - **School (Google Workspace) account:** choose **Internal**. Only people in your
     school can use it, and Google needs no review.
   - **Personal Gmail account:** Internal is greyed out, so choose **External**.
4. Contact email: your email → **Next** → tick the agreement → **Create**.
5. **External only:** open https://console.cloud.google.com/auth/audience and add your
   own email under **Test users**. If **Publish app** is available, click it: in
   *Testing* mode Google signs you out every 7 days, so you would have to sign in again
   about once a week.

## Step 4 – Download the key file

1. Open **https://console.cloud.google.com/auth/clients** → **Create client**.
2. Application type: **Desktop app**. Name: `Classroom Poster` → **Create**.
3. In the pop-up, click **Download JSON**.
4. Rename the downloaded file to **`credentials.json`** and move it into this folder,
   next to `classroom_post.py`.

## Step 5 – Sign in once

Windows: double-click **`first-sign-in.bat`**. Mac or Linux: run
`python classroom_post.py courses`.

A browser tab opens. Choose your teaching account, then click **Allow**. If you see
*Google hasn't verified this app*, click **Advanced** → **Go to Classroom Poster**: the
app is your own, so this is safe.

The terminal should then list your classes. Setup is done.

> **If you see "Access blocked: … admin"**, your school blocks this kind of app.
> Ask your Google Workspace admin to allow it.

---

## A second Google account (optional)

If you teach classes from two accounts (say a school account and a personal Gmail),
give the second one a short name, for example `home`:

1. Repeat steps 1–4 signed in as the second account. Save its key file in this folder
   as **`credentials-home.json`**.
2. Sign in once: `python classroom_post.py courses --account home`
3. From then on, add `--account home` to any command to use that account.

Without `--account`, the program uses `credentials.json` (the `default` account).

## Keep these files private

- `credentials*.json` and `token*.json` let this program post as you. Don't email
  them, put them on a shared drive or upload them to GitHub. (The `.gitignore` in this
  folder already keeps them out of git.)
- To cut off access at any time, remove *Classroom Poster* at
  https://myaccount.google.com/permissions, or delete `token.json`.

## What Google allows

- The program can only edit or delete posts that **it** made. Posts made by hand on
  the website must be changed there.
- At most 20 attachments per post.
- Uploaded files go into a Drive folder called **Classroom Poster uploads**.
