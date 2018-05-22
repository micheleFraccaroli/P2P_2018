from threading import *
from tkinter import *
import Util

class Graphics(Thread):
	def __init__(self):
		
		Thread.__init__(self)
		
	def pb(self, event):
		
		if event.num == 4:
			Util.w.yview_scroll(-1, 'units')
		elif event.num == 5:
			Util.w.yview_scroll(1, 'units')
		elif event.num == 6:
			Util.w.xview_scroll(-1, 'units')
		elif event.num == 7:
			Util.w.xview_scroll(1, 'units')

	def run(self):
		
		Util.master = Tk()

		Util.master.bind('<Button>', self.pb)

		yscrollbar = Scrollbar(Util.master)
		yscrollbar.pack(side=RIGHT, fill=Y)

		xscrollbar = Scrollbar(Util.master, orient=HORIZONTAL)
		xscrollbar.pack(side=BOTTOM, fill=X)

		masterHeight = Util.master.winfo_screenheight()
		masterWidth = Util.master.winfo_screenwidth()

		Util.w = Canvas(Util.master, width=masterWidth/2, height=masterHeight/2, scrollregion=(0, 0, masterWidth*10, masterHeight*10), yscrollcommand=yscrollbar.set, xscrollcommand=xscrollbar.set)
		Util.w.pack()

		yscrollbar.config(command=Util.w.yview)
		xscrollbar.config(command=Util.w.xview)

		Util.pause = PhotoImage(file='pause.png')
		Util.play = PhotoImage(file='play.png')
		Util.stop = PhotoImage(file='x.png')

		Util.master.mainloop()