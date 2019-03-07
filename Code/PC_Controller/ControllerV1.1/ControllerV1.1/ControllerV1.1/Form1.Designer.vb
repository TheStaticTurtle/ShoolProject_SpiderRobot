<Global.Microsoft.VisualBasic.CompilerServices.DesignerGenerated()> _
Partial Class Form1
	Inherits System.Windows.Forms.Form

	'Form remplace la méthode Dispose pour nettoyer la liste des composants.
	<System.Diagnostics.DebuggerNonUserCode()> _
	Protected Overrides Sub Dispose(ByVal disposing As Boolean)
		Try
			If disposing AndAlso components IsNot Nothing Then
				components.Dispose()
			End If
		Finally
			MyBase.Dispose(disposing)
		End Try
	End Sub

	'Requise par le Concepteur Windows Form
	Private components As System.ComponentModel.IContainer

	'REMARQUE : la procédure suivante est requise par le Concepteur Windows Form
	'Elle peut être modifiée à l'aide du Concepteur Windows Form.  
	'Ne la modifiez pas à l'aide de l'éditeur de code.
	<System.Diagnostics.DebuggerStepThrough()> _
	Private Sub InitializeComponent()
		Me.components = New System.ComponentModel.Container()
		Me.Timer1 = New System.Windows.Forms.Timer(Me.components)
		Me.Label1 = New System.Windows.Forms.Label()
		Me.Label2 = New System.Windows.Forms.Label()
		Me.Label3 = New System.Windows.Forms.Label()
		Me.Label4 = New System.Windows.Forms.Label()
		Me.Label5 = New System.Windows.Forms.Label()
		Me.Label6 = New System.Windows.Forms.Label()
		Me.Label7 = New System.Windows.Forms.Label()
		Me.Label8 = New System.Windows.Forms.Label()
		Me.Label9 = New System.Windows.Forms.Label()
		Me.Label0 = New System.Windows.Forms.Label()
		Me.SuspendLayout()
		'
		'Timer1
		'
		'
		'Label1
		'
		Me.Label1.AutoSize = True
		Me.Label1.Location = New System.Drawing.Point(96, 44)
		Me.Label1.Name = "Label1"
		Me.Label1.Size = New System.Drawing.Size(51, 17)
		Me.Label1.TabIndex = 0
		Me.Label1.Text = "Label1"
		'
		'Label2
		'
		Me.Label2.AutoSize = True
		Me.Label2.Location = New System.Drawing.Point(96, 61)
		Me.Label2.Name = "Label2"
		Me.Label2.Size = New System.Drawing.Size(51, 17)
		Me.Label2.TabIndex = 1
		Me.Label2.Text = "Label2"
		'
		'Label3
		'
		Me.Label3.AutoSize = True
		Me.Label3.Location = New System.Drawing.Point(96, 82)
		Me.Label3.Name = "Label3"
		Me.Label3.Size = New System.Drawing.Size(51, 17)
		Me.Label3.TabIndex = 2
		Me.Label3.Text = "Label3"
		'
		'Label4
		'
		Me.Label4.AutoSize = True
		Me.Label4.Location = New System.Drawing.Point(96, 103)
		Me.Label4.Name = "Label4"
		Me.Label4.Size = New System.Drawing.Size(51, 17)
		Me.Label4.TabIndex = 3
		Me.Label4.Text = "Label4"
		'
		'Label5
		'
		Me.Label5.AutoSize = True
		Me.Label5.Location = New System.Drawing.Point(96, 124)
		Me.Label5.Name = "Label5"
		Me.Label5.Size = New System.Drawing.Size(51, 17)
		Me.Label5.TabIndex = 4
		Me.Label5.Text = "Label5"
		'
		'Label6
		'
		Me.Label6.AutoSize = True
		Me.Label6.Location = New System.Drawing.Point(96, 145)
		Me.Label6.Name = "Label6"
		Me.Label6.Size = New System.Drawing.Size(51, 17)
		Me.Label6.TabIndex = 5
		Me.Label6.Text = "Label6"
		'
		'Label7
		'
		Me.Label7.AutoSize = True
		Me.Label7.Location = New System.Drawing.Point(96, 166)
		Me.Label7.Name = "Label7"
		Me.Label7.Size = New System.Drawing.Size(51, 17)
		Me.Label7.TabIndex = 6
		Me.Label7.Text = "Label7"
		'
		'Label8
		'
		Me.Label8.AutoSize = True
		Me.Label8.Location = New System.Drawing.Point(96, 187)
		Me.Label8.Name = "Label8"
		Me.Label8.Size = New System.Drawing.Size(51, 17)
		Me.Label8.TabIndex = 7
		Me.Label8.Text = "Label8"
		'
		'Label9
		'
		Me.Label9.AutoSize = True
		Me.Label9.Location = New System.Drawing.Point(96, 208)
		Me.Label9.Name = "Label9"
		Me.Label9.Size = New System.Drawing.Size(51, 17)
		Me.Label9.TabIndex = 8
		Me.Label9.Text = "Label9"
		'
		'Label0
		'
		Me.Label0.AutoSize = True
		Me.Label0.Location = New System.Drawing.Point(96, 27)
		Me.Label0.Name = "Label0"
		Me.Label0.Size = New System.Drawing.Size(51, 17)
		Me.Label0.TabIndex = 9
		Me.Label0.Text = "Label0"
		'
		'Form1
		'
		Me.AutoScaleDimensions = New System.Drawing.SizeF(8.0!, 16.0!)
		Me.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font
		Me.ClientSize = New System.Drawing.Size(800, 450)
		Me.Controls.Add(Me.Label0)
		Me.Controls.Add(Me.Label9)
		Me.Controls.Add(Me.Label8)
		Me.Controls.Add(Me.Label7)
		Me.Controls.Add(Me.Label6)
		Me.Controls.Add(Me.Label5)
		Me.Controls.Add(Me.Label4)
		Me.Controls.Add(Me.Label3)
		Me.Controls.Add(Me.Label2)
		Me.Controls.Add(Me.Label1)
		Me.Name = "Form1"
		Me.Text = "Form1"
		Me.ResumeLayout(False)
		Me.PerformLayout()

	End Sub

	Friend WithEvents Timer1 As Timer
	Friend WithEvents Label1 As Label
	Friend WithEvents Label2 As Label
	Friend WithEvents Label3 As Label
	Friend WithEvents Label4 As Label
	Friend WithEvents Label5 As Label
	Friend WithEvents Label6 As Label
	Friend WithEvents Label7 As Label
	Friend WithEvents Label8 As Label
	Friend WithEvents Label9 As Label
	Friend WithEvents Label0 As Label
End Class
