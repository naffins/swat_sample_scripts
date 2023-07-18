import time

from pycomm3 import LogixDriver

# Initialize PLC IP addresses
# So now we have IP addresses that can be referenced by PLC_IP_ADDRESSES[stage_number]["main" or "reserve"]
# eg. PLC_IP_ADDRESSES[1]["main"] for Stage 1's reserve PLC
PLC_IP_ADDRESSES = {i: {j: "192.168.1.{}{}".format(i,"0" if j=="main" else "1") for j in ("main", "reserve")} for i in range(1,7)}

# Initialize driver (this automatically opens a connection that is closed once the with block is exited)
# to connect to Stage 2
with LogixDriver(PLC_IP_ADDRESSES[2]["main"]) as driver:

    # Write to MV201 to get it to open
    # First, set the actuator to auto
    print("Setting MV201 to manual mode...")
    driver.write("HMI_MV201.Auto", False)
    
    # Next, open MV201
    # For valves this will take some time since the valves take time to travel between open and close positions
    print("Setting MV201 to open...")
    driver.write("HMI_MV201.Cmd", 2)
    input("Enter any input and press enter to continue: ")
    
    # Read status of MV201
    # Note that the value property here must be read; otherwise you will be getting a Tag object from driver.read()
    # Note also the meaning of status values for actuators:
    # - 0: closed/OFF
    # - 1: transitioning (only for valves)
    # - 2: open/ON
    # Also note that to open/turn on some actuators there are preconditions that may involve other actuators
    # eg. to turn on P101/P102, MV201 must already be open
    status = driver.read("HMI_MV201.Status").value
    print("Current status of MV201: {} ({})".format(status, "closed" if status==0 else "open" if status==1 else "transitioning"))
    input("Enter any input and press enter to continue: ")

    # Next, close MV201 and re-set auto mode
    print("Setting MV201 to close, and setting auto mode for MV201...")
    driver.write("HMI_MV201.Cmd", 1)
    driver.write("HMI_MV201.Auto", True)

    # Now we move on to sensors
    # First we read the value of a flow sensor FIT101
    value = driver.read("HMI_FIT101.Pv").value
    print("Value of HMI_FIT101.Pv: {} m^3/h".format(value))
    
    # Next, we will spoof FIT101
    # First, we turn on simulated mode for FIT101
    print("Setting FIT101 to simulated mode...")
    driver.write("HMI_FIT101.Sim", True)
    input("Enter any input and press enter to continue: ")

    # Next, we write a spoofed value for FIT101 (Note that PV in Sim_PV is all in caps here, rather than Pv)
    driver.write("HMI_FIT101.Sim_PV", 3.14159)
    print("Sleeping for 2s...")
    time.sleep(2)
    
    # Then we read both Pv and Sim_PV properties; both should return the same value in simulated mode
    print("Value of HMI_FIT101.Pv: {} m^3/h".format(driver.read("HMI_FIT101.Pv").value))
    print("Value of HMI_FIT101.Sim_PV: {} m^3/h".format(driver.read("HMI_FIT101.Sim_PV").value))
    
    # To stop spoofing for FIT101, we then disable simulated mode for FIT101
    print("Setting FIT101 to non-simulated mode...")
    driver.write("HMI_FIT101.Sim", False)

    # For non-FIT sensors, the format should be the same, though units of readings may be different, and tag properties
    # other than .Pv and .Sim_PV may be needed. Please check with one of the SWaT lab engineers.
