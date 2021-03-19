#!/usr/bin/env bash
# Global MACROS
IOC_EXE=../../bin/linux-arm/mcc118
IOC_CMD=st.cmd

# Deploy
IOC_NAME=CLFMCC
IOC_PORT=5000
IOC_DIR=/home/pi/repos/mcc118/iocBoot/iocmcc118
LAUNCH="procServ -q --noautorestart  -L ${IOC_NAME}.log -p ${IOC_NAME}.pid -n ${IOC_NAME} -i ^D^C -c ${IOC_DIR} ${IOC_PORT} ${IOC_EXE} ${IOC_CMD}"
${LAUNCH}
echo "MCC118 deployed at port $IOC_PORT" 
