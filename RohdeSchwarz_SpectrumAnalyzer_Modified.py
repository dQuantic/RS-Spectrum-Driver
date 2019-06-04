#!/usr/bin/env python

from VISA_Driver import VISA_Driver
import numpy as np

__version__ = "0.0.1"

class Error(Exception):
    pass

class Driver(VISA_Driver):
    """ This class implements the Rohde&Schwarz Network Analyzer driver"""

    def performOpen(self, options={}):
        """Perform the operation of opening the instrument connection"""
        # init meas param dict
        self.dMeasParam = {}
        # calling the generic VISA open to make sure we have a connection
        VISA_Driver.performOpen(self, options=options)


    def performSetValue(self, quant, value, sweepRate=0.0, options={}):
        """Perform the Set Value instrument operation. This function should
        return the actual value set by the instrument"""
		# create new channels if needed
        if quant.name in ('Range type',):
            if quant.getValueString(value) == 'Zero-span mode':
                # set span to zero
                self.sendValueToOther('Span', 0.0)
                self.sendValueToOther('# of points', 2.0)
                # sweep time should be set to a small value (for example, 10 ms)
                self.writeAndLog(':SWE:TIME:AUTO 0;:SWE:TIME 10E-3;')
        elif quant.name in ('Wait for new trace',):
        # if quant.name in ('Wait for new trace',):
            # do nothing
            if value == False:
                self.writeAndLog(':INIT:CONT ON;')
            pass
        else:
            # run standard VISA case 
            value = VISA_Driver.performSetValue(self, quant, value, sweepRate, options)
        return value


    def performGetValue(self, quant, options={}):
        """Perform the Get Value instrument operation"""
        # check type of quantity
        if quant.name == 'Signal':
            # check if channel is on
            if True: #quant.name in self.dMeasParam:
                # if not in continous mode, trig from computer
                bWaitTrace = self.getValue('Wait for new trace')
                bAverage = self.getValue('Average')
                # wait for trace, either in averaging or normal mode
                if bWaitTrace:
                    if bAverage:
                        nAverage = self.getValue('# of averages')
#                        self.writeAndLog(':SENS:AVER:CLE;:ABOR;:INIT;*WAI')
                        self.writeAndLog(':ABOR;:INIT:CONT OFF;:SENS:AVER:COUN %d;:INIT:IMM;*OPC' % nAverage)
                    else:
                        self.writeAndLog(':ABOR;:INIT:CONT OFF;:SENS:AVER:COUN 1;:INIT:IMM;*OPC')
                    # wait some time before first check
                    self.wait(0.03)
                    bDone = False
                    while (not bDone) and (not self.isStopped()):
                        # check if done
                        if bAverage:
#                            sAverage = self.askAndLog('SENS:AVER:COUN:CURR?')
#                            bDone = (int(sAverage) >= nAverage)
                            stb = int(self.askAndLog('*ESR?'))
                            bDone = (stb & 1) > 0
                        else:
                            stb = int(self.askAndLog('*ESR?'))
                            bDone = (stb & 1) > 0
                        if not bDone:
                            self.wait(0.1)
                    # if stopped, don't get data
                    if self.isStopped():
                        self.writeAndLog('*CLS;:INIT:CONT ON;')
                        return []
               
                
                self.writeAndLog(':INIT1:CONT ON;')
                #READ OUT IN ASCII FORMAT, WORKS BETTER
                self.write(':FORM ASCII;TRAC:DATA? TRACE1', bCheckError=False)

                sData = self.read(ignore_termination=True)
                if bWaitTrace and not bAverage:
                    self.writeAndLog(':INIT:CONT ON;')

                #WE DECODE FIRST AND THE SPLIT THE LIST INTO ITS VALUES
                splitData = sData.decode().split(',')
                #NOW WE TRANSFORM THE STRINGS INTOI FLOAT NUMBERS
                vData = [float(numeric_string) for numeric_string in splitData]
            

                startFreq = self.readValueFromOther('Start frequency')
                stopFreq = self.readValueFromOther('Stop frequency')

                #GET THE TRACE VALUES, MEANING THE vDATA LIST
                value = quant.getTraceDict(vData, x0=startFreq, x1=stopFreq)
               
                
#ADDED THIS SECTION!!
        elif quant.name == 'Signal - Zero span':

            #COPY AND PASTE
            if True: #quant.name in self.dMeasParam:
                # if not in continous mode, trig from computer
                bWaitTrace = self.getValue('Wait for new trace')
                bAverage = self.getValue('Average')
                # wait for trace, either in averaging or normal mode
                if bWaitTrace:
                    if bAverage:
                        nAverage = self.getValue('# of averages')
#                        self.writeAndLog(':SENS:AVER:CLE;:ABOR;:INIT;*WAI')
                        self.writeAndLog(':ABOR;:INIT:CONT OFF;:SENS:AVER:COUN %d;:INIT:IMM;*OPC' % nAverage)
                    else:
                        self.writeAndLog(':ABOR;:INIT:CONT OFF;:SENS:AVER:COUN 1;:INIT:IMM;*OPC')
                    # wait some time before first check
                    self.wait(0.03)
                    bDone = False
                    while (not bDone) and (not self.isStopped()):
                        # check if done
                        if bAverage:
#                            sAverage = self.askAndLog('SENS:AVER:COUN:CURR?')
#                            bDone = (int(sAverage) >= nAverage)
                            stb = int(self.askAndLog('*ESR?'))
                            bDone = (stb & 1) > 0
                        else:
                            stb = int(self.askAndLog('*ESR?'))
                            bDone = (stb & 1) > 0
                        if not bDone:
                            self.wait(0.1)
                    # if stopped, don't get data
                    if self.isStopped():
                        self.writeAndLog('*CLS;:INIT:CONT ON;')
                        return []


            self.writeAndLog(':INIT1:CONT ON;')
            self.write(':FORM ASCII;TRAC:DATA? TRACE1', bCheckError=False)
            sData = self.read(ignore_termination=True)
            sData=sData.decode()
            splitData = sData.split(',')
            vData = [float(numeric_string) for numeric_string in splitData] 
            value = np.average(vData)
            self.log(value)   
        
        #STOP COPY AND PASTE
                    
                    
        
        
        elif quant.name in ('Wait for new trace',):
               # do nothing, return local value
            value = quant.getValue()
         
    
        else:
            # for all other cases, call VISA driver
            value = VISA_Driver.performGetValue(self, quant, options)

        return value
            
    
        


if __name__ == '__main__':
    pass
