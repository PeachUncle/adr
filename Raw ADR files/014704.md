# ADR-0025: File-Uploads

## Status

Accepted

Date of decision: 2025-03-18

## Context and Problem Statement

We need the service to be able to receive uploads of files from the front end (images/ pdfs of gas and electrical safety certificates). These files need to end up in an S3 bucket where they will be virus scanned (to be considered as part of a separate ADR). There are multiple ways that files can be uploaded to S3, and we need to decide which we are going to implement.

## Considered Options

* Load file via WebApp (with WAF rule to block large uploads)
* Stream file via WebApp
* Load file via separate ECS task (with WAF rule to block large uploads)
* Stream file via separate ECS task
* Use pre-signed URLs with strict security policies
* Use pre-signed URLs with less strict security policies


## Decision Outcome

`Stream file via WebApp` (while keeping option of moving to `Stream file via separate ECS task` open if performance testing requires it), because, while it requires a more complex initial implementation than using pre-signed URLs, it is inherently more robust and so doesn't require as much work to cover off edge cases and protecting against misuse by users/ bad actors.

## Pros and Cons of the Options

### Load file via WebApp (with WAF rule to block large uploads)

We could simply load the file into memory in the WebApp and forward it to the s3 bucket. To protect against someone crashing the application by trying to upload a very large file, we could add a WAF rule that will reject the request with a redirect to a specific error page.

* Good, because the uploading is relatively simple to implement
* Good, because it allows the WebApp to handle other file validation e.g. store the fact that the user has uploaded a file, return any relevant validation errors etc
* Bad, because handling errors from large files via the WAF and a static page would either not comply with GDS standards or would be complex to implement
* Bad, because even with acceptable file sizes it could more easily cause memory/ performance issues in the main application if lots of people are attempting to upload files at once
* Neutral, because while it potentially means loading malicious code into memory there is very little risk of that code being executed in the transfer process

### Stream file via WebApp

We could stream the uploaded file into the s3 bucket through the WebApp. With careful management this would avoid the full file being loaded into memory and so would not require a separate WAF rule. 

* Good, because it allows the WebApp to handle other file validation e.g. store the fact that the user has uploaded a file, return any relevant validation errors (including the file being too large) etc
* Neutral, because it is more complex to implement, especially for checking that the size limit is not exceeded, although there is (slightly hard to find) documentation to draw on for the s3 upload, e.g. https://docs.aws.amazon.com/code-library/latest/ug/s3_example_s3_Scenario_UploadStream_section.html
* Neutral, because it could still cause some performance issues for the WebApp - these would need to be checked for during performance testing
* Neutral, because while it potentially means loading malicious code into memory there is very little risk of that code being executed in the transfer process (and less so as the file is not all loaded at once)

### Load file via separate ECS task (with WAF rule to block large uploads)

We could load the file into s3 via a separate ECS task. As with the option of loading via the WebApp, a WAF rule would be needed to check the size of the file and redirect the user if the file was too large.

* Good, because it is relatively simple to implement
* Good, because it could be initially implemented as part of the main WebApp and separated out later using Spring profiles
* Good, because it could be scaled independently to the main WebApp
* Good, because unscanned files would be isolated from the main WebApp
* [Optional] Good, because it could be combined with the virus scanning task, scanning the file in memory before transferring it to the final s3 bucket - removing the need for a more complex architecture around virus scanning.
* Good, because it could handle or report the successful upload (and scan result if applicable) either writing directly to the database or via an API call to the main WebApp
* Bad, because handling errors from large files via the WAF and a static page would either not comply with GDS standards or would be complex to implement
* Bad, because we would need robust auto-scaling rules to reduce the risk of the instance running out of memory if lots of files are uploaded at once by different users

### Stream file via separate ECS task

We could stream the file into s3 via a separate ECS task

* Good, because it could be initially implemented as part of the main WebApp and separated out later using Spring profiles
* Good, because it could be scaled independently to the main WebApp
* Good, because unscanned files would be isolated from the main WebApp
* [Optional] Good, because it could be combined with the virus scanning task, scanning the file as it is streamed before transferring it to the final s3 bucket - removing the need for a more complex architecture around virus scanning.
  * Note: Not 100% clear from the ClamAV docs whether the function that takes a stream loads/ retains the file in memory
* Neutral, because it is more complex to implement, especially for checking that the size limit is not exceeded, although there is (slightly hard to find) documentation to draw on for the s3 upload, e.g. https://docs.aws.amazon.com/code-library/latest/ug/s3_example_s3_Scenario_UploadStream_section.html
* Neutral, because while it could report validation errors back to the user this would require a subset of the WebApp code to reside to also reside in the separate ECS task
* Good, because it could handle or report the successful upload (and scan result if applicable) either writing directly to the database or via an API call to the main WebApp
* Neutral, because we would need similar auto-scaling rules to those we'd have with the main WebApp to avoid upload requests timing out

### Use pre-signed URLs with strict security policies

Instead of handling the file upload ourselves we could generate a pre-signed URL and let the user's browser use that for the file upload. This could include policies to prevent the user uploading invalid file extensions or files that are too large.

* Good, because we would not need to handle the uploaded file at all
* Good, because unscanned files would be fully isolated from our WebApp and database
* Good, because we could configure policies on the pre-signed URL to prevent the user uploading incorrect file types or files that are too large
* Good, because we can provide a url that redirects the client on successful upload
* Bad, because we cannot redirect the user if the upload policies are violated - they instead receive a generic cloudfront error
  * This could be mitigated for users with Javascript enabled by having the POST take place in Javascript, but not for those who don't
* Neutral, because it would be more complex to record any metadata about the uploaded files in the database, this would have to be reconstructed from the uploaded file

### Use pre-signed URLs with less strict security policies

To address issues about redirecting on error, we could generate a pre-signed URL with a less strict security policy that allows all file extensions and sizes of file (maybe with an extreme upper limit)

* Good, because we would not need to handle the unscanned file at all
* Good, because unscanned files would be fully isolated from the WebApp and database
* Good, because other than in extreme cases (an expired link, an extremely large file) the upload would succeed and the user would be redirected
* Neutral, because we would need a more complex endpoint to redirect to which checked the metadata of the uploaded file and then deleted it and returned the relevant validation errors if it violated any policies
* Neutral, because it would be more complex to record any metadata about the uploaded files in the database, as this would have to be reconstructed from the uploaded file
* Bad, because uploading very large file sizes or using expired links would still cause the user to see a confusing CloudFront error
  * This could be mitigated for users with Javascript enabled by having the POST take place in Javascript, but not for those who don't
* Bad, because this has more complex edge cases & race conditions to handle, e.g. someone trying to upload multiple files with the same pre-signed URL, someone POSTing from Postman instead of via the WebApp etc
