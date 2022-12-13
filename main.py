#pip install -r requirements.txt

from os import system, getcwd
from numpy import frombuffer, uint8
from cv2 import imdecode, IMREAD_COLOR, EVENT_LBUTTONUP, EVENT_LBUTTONDOWN, EVENT_MOUSEWHEEL, resize, imshow, setMouseCallback, waitKey
from ppadb.client import Client as adb

print("Starting ADB server...")
system(f"{getcwd()}\\adb\\adb.exe start-server")
print("Server started!\n")

fps = 60 # FPS is set and MOST phones have the same one
mousewheel_sens = 200 # Sensitivity when you scroll

# /!\ I advise to NOT touch from this point on.

program_name= "ADBScreen Alpha"

fps = int(1000/fps) 

client = adb(host="127.0.0.1", port=5037)

print("Debug info:\n")

def sn_handler():    
    if len(client.devices()) > 1:
        raise Exception('Please connect ONLY ONE device!')
    if len(client.devices()) < 1:
        raise Exception('Please connect AT LEAST ONE device!\n/!\ If the problem is still here, you should check if your device has ADB enabled.')
    
    
    device = client.devices()[0].serial
    return device

### video detection

def screen_detection(device):
    #if device.screencap() == None:
    #    raise "Please reconect your device and restart the program."
    screen_ba= device.screencap()
    img = frombuffer(screen_ba, uint8)
    cv_img = imdecode(img, IMREAD_COLOR)
    height = cv_img.shape[0]
    width = cv_img.shape[1]
    return cv_img, height, width

def screen_input(event, x, y, flags, params):
    global device, x1, y1, x2, y2, mousewheel_sens
    adb_cmd = None

    if event == EVENT_LBUTTONDOWN:
        x1, y1 = x*3, y*3
        #print(f"x1:{x1} y1:{y1}")

    if event == EVENT_LBUTTONUP:
        x2, y2 = x*3, y*3
        #print(f"x2:{x2} y2:{y2}")
        if x1 == x2 and y1 == y2:
            adb_cmd = f"input tap {x1} {y1}"
        else:
            adb_cmd = f"input swipe {x1} {y1} {x2} {y2}"

    if event == EVENT_MOUSEWHEEL:
        if flags > 0:
            adb_cmd = f"input swipe {x} {y} {x} {y+mousewheel_sens}"
        else:
            adb_cmd = f"input swipe {x} {y} {x} {y-mousewheel_sens}"
    
    if adb_cmd != None:
        print(f"adb shell {adb_cmd}")
        device.shell(adb_cmd)

def show_screen(img, resized_height, resized_width):
    global fps, program_name
    image = resize(img, (resized_width, resized_height))
    imshow(program_name, image) 
    setMouseCallback(program_name, screen_input)
    waitKey(fps)

###
    
def main():  
    global device, resized_height, resized_width
    try:
        sn = sn_handler()
        device = client.device(sn)

        img, height, width = screen_detection(device)
        resized_height, resized_width = int(height/3), int(width/3)
        print(f"model: {sn}; resolution: {height, width} >>[RESIZE]>> {resized_height, resized_width}\n"+"="*75)

        while True:
            img, height, width = screen_detection(device)
            resized_height, resized_width = int(height/3), int(width/3)
            show_screen(img, resized_height, resized_width)

    except Exception as e:
        input(f"Exception: {e}")
        system(f"{getcwd()}\\adb\\adb.exe kill-server")
        return

if __name__=="__main__":       
    main()