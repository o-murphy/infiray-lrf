try:
    import run
except (Exception, KeyboardInterrupt) as exc:
    print("FATAL: ", exc)
    is_rem_run = input("Remove broken run.py?")
    if is_rem_run == 'yes':
        import os
        os.remove('run.py')
