import os
import win32com.client as win32


def init_aspen():
    print('Connecting to Aspen Plus App')
    aspen = win32.Dispatch('Apwn.Document')
    aspen.InitFromArchive2(os.path.abspath(r'C:\Users\c160102\Downloads\basecase.bkp'))
    return aspen
