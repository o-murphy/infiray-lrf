
try:
    import run
except Exception as exc:
    print("FATAL: ", exc)
    import os
    os.remove('run.py')
