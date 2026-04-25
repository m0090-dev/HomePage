eec run -t dev -p python -a "./index.py" 
eec run -t dev -p git -a "add","."
eec run -t dev -p git -a "commit","-m","'Update'"
eec run -t dev -p git -a "push","origin","main"
pause
