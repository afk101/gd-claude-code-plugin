---
name: upload-to-QCDN
description: This skill should be used when the user wants to "upload files to qcdn", "upload images to qcdn", "host files on qcdn", or mentions "uploading to image host".
version: 1.0.0
---

# Upload to QCDN

This skill provides functionality to upload local files to the QCDN image hosting service using the `@q/qcdn` library.

## Usage

To upload files, use the bundled script `scripts/upload.js`.

### Prerequisites

Before using this skill for the first time, install the dependencies:

```bash
cd ~/.claude/skills/upload-to-qcdn
npm install
```

### Uploading Files

Execute the script with the paths of the files you want to upload:

```bash
node ~/.claude/skills/upload-to-qcdn/scripts/upload.js <path-to-file1> [path-to-file2] ...
```

The script accepts one or more file paths (relative or absolute).

### Output

The script outputs a JSON object where keys are local file paths and values are the remote URLs.

Example output:
```json
{
  "/Users/username/images/logo.png": "https://p0.ssl.qhimg.com/t01abcd.png",
  "/Users/username/images/banner.jpg": "https://p0.ssl.qhimg.com/t01efgh.jpg"
}
```

## Implementation Details

The upload script uses the following configuration options:
- **https**: true (Use HTTPS)
- **min**: true (Enable compression)
- **force**: true (Ignore errors)
- **keepName**: false

The underlying library used is `@q/qcdn`.
