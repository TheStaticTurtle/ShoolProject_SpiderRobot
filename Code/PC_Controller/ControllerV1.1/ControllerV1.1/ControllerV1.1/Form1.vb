Imports System.Runtime.InteropServices

Public Class Form1

	Declare Function joyGetPosEx Lib "winmm.dll" (ByVal uJoyID As Integer, ByRef pji As JOYINFOEX) As Integer

	<StructLayout(LayoutKind.Sequential)>
	Public Structure JOYINFOEX
		Public dwSize As Integer
		Public dwFlags As Integer
		Public dwXpos As Integer
		Public dwYpos As Integer
		Public dwZpos As Integer
		Public dwRpos As Integer
		Public dwUpos As Integer
		Public dwVpos As Integer
		Public dwButtons As Integer
		Public dwButtonNumber As Integer
		Public dwPOV As Integer
		Public dwReserved1 As Integer
		Public dwReserved2 As Integer
	End Structure

	Dim myjoyEX As JOYINFOEX

	Private Sub Timer1_Tick(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles Timer1.Tick

		' Get the joystick information
		Call joyGetPosEx(0, myjoyEX)

		With myjoyEX
			Label0.Text = .dwXpos.ToString          'Up to six axis supported
			Label1.Text = .dwYpos.ToString
			Label2.Text = .dwZpos.ToString
			Label3.Text = .dwRpos.ToString
			Label4.Text = .dwUpos.ToString
			Label5.Text = .dwVpos.ToString
			Label6.Text = .dwButtons.ToString("X")  'Print in Hex, so can see the individual bits associated with the buttons
			Label7.Text = .dwButtonNumber.ToString  'number of buttons pressed at the same time
			Label8.Text = (.dwPOV / 100).ToString     'POV hat (in 1/100ths of degrees, so divided by 100 to give degrees)
		End With
	End Sub

	Private Sub Form1_Load(ByVal sender As System.Object, ByVal e As System.EventArgs) Handles MyBase.Load
		myjoyEX.dwSize = 64
		myjoyEX.dwFlags = &HFF ' All information
		Timer1.Interval = 200  'Update at 5 hz
		Timer1.Start()
	End Sub
End Class
