import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import tkinter.messagebox as messagebox
from PIL import Image, ImageTk
import struct

def update_com_ports(event=None):
    combox_com_port['values'] = get_available_ports()

def get_available_ports():
    ports = list(serial.tools.list_ports.comports())
    return [f"{p.device} - {p.description}" for p in ports]

def toggle_mode(value):
    if value == "UI":
        send_command("Switch to UI")
    else:
        send_command("Switch to STM32")

def send_command(command_byte, channel, target):
    # Make sure the target value fits in 2 bytes
    if target > 0xFFFF:
        target = 0xFFFF
    
    command_packet = bytes([command_byte, channel,
                            (target >> 8) & 0xFF,
                            target & 0xFF])

    hex_command_packet = ' '.join(f"0x{byte:02X}" for byte in command_packet)
    console.insert(tk.END, f"Sent: {hex_command_packet}\n")
    console.see(tk.END)

    ser.write(command_packet)

def position_slider_command(val, i):
    if motor_vars[i].get():
        target_position = int(round(float(val)))  # Convert the float to an integer
        send_command(0x01, i+1, target_position)

def accel_slider_command(val, i):
    if motor_vars[i].get():
        target_accel = int(round(float(val)))  # Convert the float to an integer
        send_command(0x02, i+1, target_accel)  # 0x02 is a placeholder for your actual command byte

def speed_slider_command(val, i):
    if motor_vars[i].get():
        target_speed = int(round(float(val)))  # Convert the float to an integer
        send_command(0x03, i+1, target_speed)  # 0x03 is a placeholder for your actual command byte

def hand_position(pos):
    positions = {
        "Pointing": 0x10,
        "Fist": 0x11,
        "Rock!": 0x12,
        "Fuck": 0x13,
        "Thumb": 0x14,
        "Open": 0x15
    }
    command_byte = positions.get(pos)
    if command_byte is not None:
        send_command(command_byte, 0x00, 0x0000)

def connect_com_port():
    global ser
    port_with_description = combox_com_port.get()

    # Extract just the COM port name
    port = port_with_description.split(' - ')[0]
    
    if port_with_description == "Connect to device" or port_with_description not in combox_com_port['values']:
        messagebox.showerror("Connection Error", "Please select a valid serial port.")
        return

    try:
        if ser:
            ser.close()
        ser = serial.Serial(port, 115200)
        print("Is Open:", ser.is_open)
        console.insert(tk.END, f"Connected to {port}\n")
        enable_controls(True)
    except Exception as e:
        if ser:
            ser = None
        console.insert(tk.END, f"Failed to connect to {port}\n")
        messagebox.showerror("Error", f"Failed to connect to {port}\nException: {e}")

def enable_controls(status):
    for widget in all_controls:
        if status:
            widget.config(state=tk.NORMAL)
        else:
            widget.config(state=tk.DISABLED)

def send_inputbox_command():
    command = input_command_var.get()
    if command:
        send_command(command)
        input_command_var.set("")  # Clear the input box

def resize_image(input_image_path, percentage):
    original_image = Image.open(input_image_path)
    w, h = original_image.size
    new_width = int(w * percentage / 100)
    new_height = int(h * percentage / 100)
    resized_image = original_image.resize((new_width, new_height), 3)
    return ImageTk.PhotoImage(resized_image)

# Create main window
root = tk.Tk()
root.title("Prosthetic Hand Control")
root.geometry("860x540")  # Adjusted size

# Create Notebook (Tab holder)
notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=1)

# Create frames for each tab
main_frame = ttk.Frame(notebook)
help_frame = ttk.Frame(notebook)

# Add frames to notebook (tabs)
notebook.add(main_frame, text='Main')
notebook.add(help_frame, text='Help')

# Inside 'help_frame', add your image and text instructions
img = resize_image("Forearm.png", 25)  # Replace with your image path and resize percentage
img_label = tk.Label(help_frame, image=img)
img_label.image = img
img_label.pack()

instruction_text = """Here are some instructions:
1. Connect to the COM port.
2. Choose the mode.
3. Control the motors.
"""
instruction_label = tk.Label(help_frame, text=instruction_text)
instruction_label.pack()

# Setup for COM Port Selector
ports_var = tk.StringVar()
ports_var.set("Connect to device")  # set default text for combobox

# COM Port Selector and Connect button
ttk.Label(main_frame, text="COM Port:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
combox_com_port = ttk.Combobox(main_frame, values=get_available_ports(), textvariable=ports_var)
combox_com_port.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
ttk.Button(main_frame, text="Connect", command=connect_com_port).grid(row=1, column=2, padx=5, pady=5)
combox_com_port.bind('<Button-1>', update_com_ports)

# Mode Switch
mode_var = tk.StringVar(value="STM32")
ttk.Label(main_frame, text="Mode:").grid(row=1, column=3, padx=5, pady=5, sticky='e')

ui_mode_radiobutton = ttk.Radiobutton(main_frame, text="UI", variable=mode_var, value="UI", command=lambda: toggle_mode(mode_var.get()))
ui_mode_radiobutton.grid(row=1, column=4, padx=2, pady=5)

stm32_mode_radiobutton = ttk.Radiobutton(main_frame, text="STM32", variable=mode_var, value="STM32", command=lambda: toggle_mode(mode_var.get()))
stm32_mode_radiobutton.grid(row=1, column=5, padx=2, pady=5)

# Headers for Enable, Position, Acceleration, Speed and Hand Positions
ttk.Label(main_frame, text="Enable").grid(row=2, column=0, sticky='w', padx=5, pady=5)
ttk.Label(main_frame, text="Position").grid(row=2, column=2, sticky='w', padx=5, pady=5)
ttk.Label(main_frame, text="Speed").grid(row=2, column=4, sticky='w', padx=5, pady=5)
ttk.Label(main_frame, text="Acceleration").grid(row=2, column=6, sticky='w', padx=5, pady=5)
ttk.Label(main_frame, text="Hand Position").grid(row=2, column=9, sticky='w', padx=5, pady=5)


position_sliders = []
accel_sliders = []
speed_sliders = []
checkbuttons = []



# Motor Sliders, checkboxes, and labels
motor_vars = []
for i in range(6):  # assuming 5 motors
    motor_var = tk.BooleanVar()

    ttk.Label(main_frame, text=f"Motor {i+1}").grid(row=i+3, column=0, sticky='w', padx=5, pady=5)
    
    cb = ttk.Checkbutton(main_frame, variable=motor_var)
    cb.grid(row=i+3, column=1, padx=5, pady=5)
    checkbuttons.append(cb)
    
    pos_slider = ttk.Scale(main_frame, from_=250, to_=1700, length=150, command=lambda val, i=i: position_slider_command(val, i))
    pos_slider.grid(row=i+3, column=2, columnspan=2, padx=5, pady=5)
    position_sliders.append(pos_slider)

    # Acceleration slider for each motor
    accel_slider = ttk.Scale(main_frame, from_=250, to_=1700, length=150, command=lambda val, i=i: accel_slider_command(val, i))
    accel_slider.grid(row=i+3, column=4, columnspan=2, padx=5, pady=5)
    accel_sliders.append(accel_slider)

    # Speed slider for each motor
    speed_slider = ttk.Scale(main_frame, from_=250, to_=1700, length=150, command=lambda val, i=i: speed_slider_command(val, i))
    speed_slider.grid(row=i+3, column=6, columnspan=2, padx=5, pady=5)
    speed_sliders.append(speed_slider)

    motor_vars.append(motor_var)


position_buttons = []
# Shifting the position buttons to the rightmost column
positions = ["Pointing", "Fist", "Rock!", "Fuck", "Thumb", "Open"]  # Add other positions as required
for idx, pos in enumerate(positions, start=1):
    btn = ttk.Button(main_frame, text=f"{pos}", command=lambda pos=pos: hand_position(pos))
    btn.grid(row=idx+2, column=9, padx=5, pady=5, sticky='ew')
    position_buttons.append(btn)

# Inserting the vertical separator between sliders and position buttons
separator = ttk.Separator(main_frame, orient='vertical')
separator.grid(row=3, column=8, rowspan=len(positions)+1, sticky='ns', padx=5)


# Console label, area, and scrollbar
ttk.Label(main_frame, text="Console").grid(row=9, column=0, sticky='w', padx=5, pady=5)

# Creating a frame to contain the Text widget and Scrollbar
console_frame = ttk.Frame(main_frame)
console_frame.grid(row=10, column=0, columnspan=6, padx=5, pady=5, sticky='ew')

console = tk.Text(console_frame, height=10, width=40, wrap=tk.WORD)
scrollbar = ttk.Scrollbar(console_frame, orient=tk.VERTICAL, command=console.yview)

console.config(yscrollcommand=scrollbar.set)

console.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Command Input Box, entry, and send button

input_command_var = tk.StringVar()
input_box = ttk.Entry(main_frame, textvariable=input_command_var, width=50)
input_box.grid(row=11, column=0, columnspan=5, sticky='ew', padx=5, pady=5)

send_button = ttk.Button(main_frame, text="Send", command=send_inputbox_command)
send_button.grid(row=11, column=5, padx=4, pady=4)

# Binding Enter key to the send function
input_box.bind('<Return>', lambda event=None: send_inputbox_command())

# List of all controls to enable/disable based on connection status
all_controls = checkbuttons + position_sliders + accel_sliders + speed_sliders + position_buttons + [input_box, send_button] + [ui_mode_radiobutton, stm32_mode_radiobutton]

# Initially disable all controls
enable_controls(False)

# Start with serial connection as None
ser = None

root.mainloop()

# Close the serial port when the application exits
if ser:
    ser.close()