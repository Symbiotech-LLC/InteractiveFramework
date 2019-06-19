# Encode Password
## Summary:
Module that Encodes and Decodes Password using a secret key and SHA-256 Encoding. <br>
script name: `encode_password.py` <br>

__What Does the Module do?:__ <br>

* Encode Password and return result so it can't be viewed in plain text
    * Perfect for storing in databases for extra security
* Decode Password and return plain text result
    * Perfect for decoding passwords stored securely in databases

## Prerequisites:

None

## Arguments:
  Argument   |     CommandLine Flag   |   Description
------------ | ------------- | -------------
Encode | --encode, -encode | Encodes a string
Decode | --decode, -decode | Decodes Encoded String