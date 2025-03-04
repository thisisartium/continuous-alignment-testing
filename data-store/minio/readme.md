## Example of posting data


```bash
curl -X PUT -T "sample.zip" \
    -H "Host: localhost:9000" \
    -H "Date: $(date -R)" \
    -H "Content-Type: application/zip" \
    -H "Authorization: AWS minioadmin:minioadmin" \
    http://localhost:9000/test-results/sample.zip
```

if you get `SignatureDoesNotMatch` error, adjust bucket policy to allow public access to the bucket.


## Install client

on macOS:

```bash
brew install minio/stable/mc
mc alias set myminio http://localhost:9000 minioadmin minioadmin

Added `myminio` successfully.
```

copy files to minio:

```bash
mc cp sample.zip myminio/test-results

...gnment-testing/sample.zip: 14.09 KiB / 14.09 KiB  ▓▓▓▓▓▓▓
```
