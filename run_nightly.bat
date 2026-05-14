@echo off
cd /d "c:\Users\Admin\Documents\Project 3_Lead Gen"
python organize_sheets.py >> logs\nightly.log 2>&1
