@echo off
IF EXIST env\ (
echo ---- found virtual environment
echo ---- collecting python libraries and run in venv ..
cmd /k "env\Scripts\activate & pip install -r requirements.txt -U & python run.py"

) ELSE (
echo ---- no virtual environment found
rd /s /q "env"
echo ---- creating venv now, it might take a while ... please wait 
python -m venv env
echo ---- venv installed
echo ---- collecting python libraries and run in venv ..
cmd /k "env\Scripts\activate & pip install -r requirements.txt -U & python run.py"
)