from cefpython3 import cefpython as cef
import platform
import sys
import numpy as np
import cv2

VIEWPORT_SIZE = (1280, 720)
FRAMERATE = 30
URL = ''

class RenderHandler(object):
    def __init__(self):
        self.OnPaint_called = False

    def GetViewRect(self, rect_out, **_):
        """Called to retrieve the view rectangle which is relative
        to screen coordinates. Return True if the rectangle was
        provided."""
        # rect_out --> [x, y, width, height]
        rect_out.extend([0, 0, VIEWPORT_SIZE[0], VIEWPORT_SIZE[1]])
        return True

    def OnPaint(self, browser, element_type, paint_buffer, **_):
        if element_type == cef.PET_VIEW:
            buffer_string = paint_buffer.GetBytes(mode="bgra",
                                                  origin="top-left")
            img = np.frombuffer(buffer_string, dtype=np.uint8, count=(VIEWPORT_SIZE[0]*VIEWPORT_SIZE[1]*4)).reshape((VIEWPORT_SIZE[1],VIEWPORT_SIZE[0],4))
            cv2.imshow('frame', img)

def check_versions():
    ver = cef.GetVersion()
    print("CEF Python {ver}".format(ver=ver["version"]))
    print("Chromium {ver}".format(ver=ver["chrome_version"]))
    print("CEF {ver}".format(ver=ver["cef_version"]))
    print("Python {ver} {arch}".format(
           ver=platform.python_version(),
           arch=platform.architecture()[0]))
    assert cef.__version__ >= "57.0", "CEF Python v57.0+ required to run this"

def command_line_arguments():
    if len(sys.argv) == 2:
        url = sys.argv[1]
        if url.startswith("http://") or url.startswith("https://"):
            global URL
            URL = url+'&codec=vp9'
        else:
            print("Error: Invalid url argument")
            sys.exit(1)

    elif len(sys.argv) > 1:
        print("Expected arguments: url")
        sys.exit(1)

def create_browser(settings):
    # Create browser in off-screen-rendering mode (windowless mode)
    # by calling SetAsOffscreen method. In such mode parent window
    # handle can be NULL (0).
    parent_window_handle = 0
    window_info = cef.WindowInfo()
    window_info.SetAsOffscreen(parent_window_handle)
    print(f"Viewport size: {VIEWPORT_SIZE}")
    print(f"Loading url: {URL}")
    browser = cef.CreateBrowserSync(window_info=window_info,
                                    settings=settings,
                                    url=URL)
    browser.SetClientHandler(RenderHandler())
    browser.SendFocusEvent(True)
    # You must call WasResized at least once to let know CEF that
    # viewport size is available and that OnPaint may be called.
    browser.WasResized()

def main():
    check_versions()
    sys.excepthook = cef.ExceptHook  # To shutdown all CEF processes on error
    command_line_arguments()
    # Off-screen-rendering requires setting "windowless_rendering_enabled"
    # option.
    settings = {
        "windowless_rendering_enabled": True,
    }
    switches = {
        # GPU acceleration is not supported in OSR mode, so must disable
        # it using these Chromium switches (Issue #240 and #463)
        "disable-gpu": "",
        "disable-gpu-compositing": "",
        # Tweaking OSR performance by setting the same Chromium flags
        # as in upstream cefclient (Issue #240).
        "enable-begin-frame-scheduling": "",
        "disable-surfaces": "",  # This is required for PDF ext to work
    }
    browser_settings = {
        # Tweaking OSR performance (Issue #240)
        "windowless_frame_rate": 30,  # Default frame rate in CEF is 30
    }
    cef.Initialize(settings=settings, switches=switches)
    create_browser(browser_settings)
    cef.MessageLoop()
    cef.Shutdown()


if __name__ == '__main__':
    main()
