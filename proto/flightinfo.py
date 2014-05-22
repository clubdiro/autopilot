#!/usr/bin/env python
# encoding: utf-8

from collections import deque
import matplotlib
matplotlib.use('TkAgg')
matplotlib.rcParams['toolbar'] = 'None'
import matplotlib.pyplot as plt
import multiprocessing as mp
import sys
import time

MAX_DATA_LEN = 60

"""
Affiche les informations de vol.
"""
class FlightInfo:
    def __init__(self, fig, rownum, colnum, pos, title='Untitled', height=0.0,
                 legend=None, xlims=[0, 180], ylims=[0, 500]):

        self.title = title
        self.redraw = False
        self.pos = pos
        self.fig = fig
        self.neg = ylims[0] < 0

        self.sub = fig.add_subplot(rownum, colnum, pos)
        self.sub.yaxis.tick_right()
        self.sub.set_ymargin(0.15)
        if legend != None:
            plt.legend(legend)
        plt.title(title)
        self.sub.set_ylim(ylims)
        self.sub.set_xlim(xlims)
        self.xlims = xlims
        self.ylims = ylims
        #Ajouter la ligne suivante si les performances sont mauvaises.
        #self.sub.get_xaxis().set_visible(False)
        #Enlever la ligne suivante si les performances sont mauvaises.
        plt.grid()

        self.start = -1
        self.xdata = deque([0])
        self.ydata = deque([height])
        self.line, = self.sub.plot([], [], '-r')
        self.fig.canvas.draw()
        self.bg = self.fig.canvas.copy_from_bbox(self.sub.bbox)


    """
    Retourne le sous-tracé à son format original.
    """
    def re_init(self):
        self.start = self.platform_time()
        xlims = self.xlims
        ylims = self.ylims
        
        self.sub.set_xlim(xlims[0], xlims[1])
        self.sub.set_ylim(ylims[0], ylims[1])
        
        self.xdata.clear()
        self.xdata = deque([0])
        self.ydata.clear()
        self.ydata = deque([0])

    """
    Force la figure à s'actualiser. Attention, très lent.
    """
    def force_draw(self):
        self.fig.canvas.draw()
    
    """
    Dessine le graphe.
    """
    def draw(self, bg=False):
        if (bg):
            self.fig.canvas.restore_region(self.bg)
        self.sub.draw_artist(self.line)
        self.fig.canvas.blit(self.sub.bbox)

    """
    Actualise le sous-tracé avec la valeur donnée.
    Redessine si "redraw" est vrai.
    """
    def update(self, ydata):
        if self.start < 0:
            self.start = self.platform_time()
        if type(ydata) is not list:
            ydata = [ydata]

        if len(ydata) > 0:
            self.xdata.append(self.timespan())
            self.ydata.append(ydata.pop())
            self.line.set_data([self.xdata, self.ydata])

        relim = self._trim()
        if self.redraw:
            self.draw(relim)
        return relim

    """
    Élimine les valeurs superflues et reformate.
    """
    def _trim(self):
        ylims = self.sub.get_ylim()
        xlims = self.sub.get_xlim()
        outx = self.xdata[-1] > xlims[1]
        downy = self.ydata[-1] < ylims[0]
        overy = self.ydata[-1] > ylims[1]
        #Si une valeur "aberrante" empêche la bonne mise à l'échelle, elle
        #est retirée.
        if (len(self.ydata) > MAX_DATA_LEN or
            abs(self.ydata[0] - self.ydata[1]) > 150):
            self.ydata.popleft()
            self.xdata.popleft()
        #Gère le redessinage et la mise à jour de l'échelle.
        if outx:
            upbnd = xlims[1] + abs(xlims[1] - xlims[0])//2
            lwbnd = xlims[1] - abs(xlims[1] - xlims[0])//2
            self.sub.set_xlim(lwbnd, upbnd)
        if downy:
            lwbnd = self.ydata[-1] - abs(ylims[1] - ylims[0])//2
            if not self.neg and lwbnd < 0:
                upbnd = ylims[0] + abs(ylims[1] - ylims[0])
                lwbnd = 0
            else:
                upbnd = self.ydata[-1] + abs(ylims[1] - ylims[0])//2
            self.sub.set_ylim(lwbnd, upbnd)
        elif overy:
            upbnd = self.ydata[-1] + abs(ylims[1] - ylims[0])//2
            lwbnd = self.ydata[-1] - abs(ylims[1] - ylims[0])//2
            self.sub.set_ylim(lwbnd, upbnd)
        return downy or overy or outx

    """
    Fonction débogue.
    """
    def printcoord(self):
        print ('Linex: {0}, Liney: {1}'.format(self.xdata[-1],self.ydata[-1]))

    """
    Retourne le temps écoulé depuis le début du traçage.
    """
    def timespan(self, time=-1):
        if time < 0:
            time = self.start
        return self.platform_time() - time

    """
    Détermine si les informations vont se redessiner lors de la mise à jour.
    """
    def redraw_on_update(self, redraw=True):
        self.redraw = redraw

    """
    Actualise le background pour le réaffichage. On cache d'abord toutes les
    lignes. Puis on redescine l'arrière plan du graphe et on le garde comme
    référence. Finalement on remet les lignes cachées. Cacher les lignes n'est
    pas nécessaire pour les graphes qui varient peu.
    """
    def refresh_bg(self):
        for line in self.sub.lines:
            line.set_visible(False)
        self.fig.canvas.draw()
        self.bg = self.fig.canvas.copy_from_bbox(self.sub.bbox)
        for line in self.sub.lines:
            line.set_visible(True)

    """
    Retourne la meilleure mesure du temps sur le système de l'utilisateur.
    """
    def platform_time(self):
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            return time.clock()
        else:
            return time.time()

    """
    Arrête le calcul de la courbe.
    """
    def terminate(self):
        plt.close('all')

FRAMES_UNTIL_REFRESH = 5
resize = False

"""
Contient les sous-tracés et gère leur placement.
"""
class DashBoard(FlightInfo):
    def __init__(self, title='Untitled', height=0.0, legend=None, colsize=2,
                 ylims=[0, 500]):
        self.lims = ylims
        self.title = title
        self.frames = 0
        if sys.platform == 'win32' or sys.platform == 'cygwin':
            self.redraw = False
        else:
            self.redraw = True
        self.start = -1
        self.lastupdate = self.platform_time()
        if colsize > 0:
            self.colsize = colsize
        else:
            self.colsize = 2
        self.fig = plt.figure()
        self.fig.show()

        def on_resize(event):
            global resize
            resize = True

        self.fig.canvas.mpl_connect('resize_event', on_resize)

        flinfo = FlightInfo(self.fig, 1, 1, 1, title, height, legend, ylims=ylims)
        flinfo.redraw_on_update(self.redraw)
        self.plots = [flinfo]

    """
    Créé un nouveau sous-tracé.
    """
    def add(self, title='Untitled', height=0.0, legend=None, ylims=[0,500]):
        size = len(self.plots)
        rowsize = (size//self.colsize)+1

        if size < self.colsize or rowsize-1 * self.colsize < size:
            for i in range(size):
                plot = self.plots[i]
                plot.sub.change_geometry(rowsize, self.colsize, i+1)

        flinfo = FlightInfo(self.fig, rowsize, self.colsize, size+1, title,
                            height, legend, ylims=ylims)
        flinfo.redraw_on_update(self.redraw)
        self.plots.append(flinfo)

        plt.tight_layout()
        self.fig.canvas.draw()

        for plot in self.plots:
            plot.refresh_bg()

        plt.pause(0.0001)
        return flinfo
    
    """
    Remets les valeurs à leurs valeurs initiales.
    """
    def re_init(self):
        self.frames = 0
        for plot in self.plots:
            plot.re_init()
        self.fig.canvas.draw()

    """
    Retourne le tracé à la position donnée (dernier ajouté par défaut).
    """
    def get(self,index=-1):
        return self.plots[index]

    """
    Fait la mise à jour de l'objet à pos. (initial par défaut)
    """
    def update(self, ydata, pos=0):
        self.frames = self.frames + 1
        val = self.plots[pos].update(ydata)
        return val
    
    """
    Fait la mise à jours tous les sous tracés à partir de la liste de données.
    """
    def update_all(self, ydatas):
        global resize
        if resize:
            resize = False
            for plot in self.plots:
                plot.refresh_bg()
        if self.lastupdate > 0 and self.timespan(self.lastupdate) >= 1:
            drawall = False
            if len(ydatas) == len(self.plots):
                for x in self.plots:
                    drawall = x.update(ydatas.popleft()) or drawall
            self.lastupdate = self.platform_time()
            #Pause permet la loop des événements de clicks, etc de se produire.
            #En même temps, elle redessine le frame. (Windows)
            if (sys.platform == 'win32' or sys.platform == 'cygwin' and 
                not self.frames % FRAMES_UNTIL_REFRESH):
                    plt.pause(.000001)
            #Pour les autres OS, suffit de redessiner si nécessaire.
            elif drawall:
                self.fig.canvas.draw()
