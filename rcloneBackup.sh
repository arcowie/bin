#!/bin/bash
rclone sync /home/arcowie/Documents googleDrive:desktopBackup/Documents --transfers=32 -v --log-file=/var/log/backupDocuments.txt
rclone sync /home/arcowie/research googleDrive:desktopBackup/research --transfers=32 -v --log-file=/var/tmp/backupResearch.txt

