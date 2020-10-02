#! /bin/bash
aws s3 sync ./temp/ s3://mlearn-input/ --delete
