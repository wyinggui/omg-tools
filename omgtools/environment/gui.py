from environment import Environment, Obstacle
from ..basics.shape import Rectangle, Circle

import Tkinter as tk
import pickle

class EnvironmentGUI(tk.Frame):
    # Graphical assistant to make an environment
    # width = environment border width
    # height = environment border height
    # position = top left corner point of environment
    def __init__(self, parent, width=8,height=8, position=[0,0], options=None, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)

        self.root = parent
        self.root.title("Environment")
        self.root.resizable(0,0)

        self.meter_to_pixel = 50  # conversion of meter to pixels

        cell_size = options['cell_size'] if 'cell_size' in options else 0.5

        # make environment frame and size it
        self.frame_width = width*self.meter_to_pixel
        self.frame_height = height*self.meter_to_pixel
        self.position = [pos * self.meter_to_pixel for pos in position]  # top left corner point of the frame
        self.canvas = tk.Canvas(self.root, width=self.frame_width, height=self.frame_height, borderwidth=0, highlightthickness=0)
        self.canvas.configure(cursor="tcross")
        self.canvas.grid(row=0,columnspan=3)
        self.cell_width = int(cell_size*self.meter_to_pixel)  # in pixels, so int is required
        self.cell_height = int(cell_size*self.meter_to_pixel)
        self.rows = self.frame_width/self.cell_width
        self.columns = self.frame_height/self.cell_height

        # draw grid
        self.rect = {}
        for column in range(self.columns):
            for row in range(self.rows):
                x1 = column*self.cell_width
                y1 = row * self.cell_height
                x2 = x1 + self.cell_width
                y2 = y1 + self.cell_height
                self.rect[row,column] = self.canvas.create_rectangle(x1,y1,x2,y2, fill="white", tags="rect")

        self.obstacles = []  # list to hold all obstacles
        self.clicked_positions = []  # list to hold all clicked positions

        self.canvas.bind("<Button-1>", self.make_obstacle)  # left mouse button makes obstacle
        self.canvas.bind("<Button-3>", self.get_position)  # right mouse button gives a position

        # Add buttons
        self.ready_button = tk.Button(self.root, text="Ready", fg="green", command=self.build_environment)
        self.ready_button.grid(row=2, column=0)

        self.quit_button = tk.Button(self.root, text="Quit", fg="red", command=self.canvas.quit)
        self.quit_button.grid(row=3, column=0)

        self.remove_button = tk.Button(self.root, text="Remove", fg="black", command=self.remove_last_obstacle)
        self.remove_button.grid(row=4, column=0)

        self.load_button = tk.Button(self.root, text="Load", fg="black", command=self.load_environment)
        self.load_button.grid(row=5, column=0)

        self.save_env = tk.BooleanVar(value=False)
        label_save = tk.Checkbutton(self.root, text="Save [yes/no]", variable=self.save_env)
        label_save.grid(row=7,column=0)

        # add cell_size button
        self.cell_size = tk.Label(self.root, text='Cell size: ' + str(cell_size) + 'x' + str(cell_size) + ' [m]')
        self.cell_size.grid(row=1, column=1)

        # Clicked position label
        # self.clickedPos = tk.StringVar()
        # labelClickedPos = tk.Label(self, text="Clicked position [x,y]")
        # labelClickedPosEntry = tk.Entry(self, bd =0, textvariable=self.clickedPos)
        # labelClickedPos.pack()
        # labelClickedPosEntry.pack()

        # Add rectangle or circle
        self.shape = tk.StringVar()
        self.circle_button = tk.Radiobutton(self.root, text="Circle", variable=self.shape, value='circle')
        self.circle_button.grid(row=2, column=2)
        self.rectangle_button = tk.Radiobutton(self.root, text="Rectangle", variable=self.shape, value='rectangle')
        self.rectangle_button.grid(row=3,column=2)

        # Add text
        self.width = tk.DoubleVar()
        self.height = tk.DoubleVar()
        self.radius = tk.DoubleVar()

        label_width = tk.Label(self.root, text="Width [m]")
        label_width_entry = tk.Entry(self.root, bd =0, textvariable=self.width)
        label_width.grid(row=2,column=1)
        label_width_entry.grid(row=3,column=1)

        label_height = tk.Label(self.root, text="Height [m]")
        label_height_entry = tk.Entry(self.root, bd =0, textvariable=self.height)
        label_height.grid(row=4,column=1)
        label_height_entry.grid(row=5,column=1)

        label_radius = tk.Label(self.root, text="Radius [m]")
        label_radius_entry = tk.Entry(self.root, bd =0, textvariable=self.radius)
        label_radius.grid(row=6,column=1)
        label_radius_entry.grid(row=7,column=1)

        self.vel_x = tk.DoubleVar(value=0.0)
        self.vel_y = tk.DoubleVar(value=0.0)

        label_velx = tk.Label(self.root, text="x-velocity [m/s]")
        label_velx_entry = tk.Entry(self.root, bd =0, textvariable=self.vel_x)
        label_velx.grid(row=4,column=2)
        label_velx_entry.grid(row=5,column=2)

        label_vely = tk.Label(self.root, text="y-velocity [m/s]")
        label_vely_entry = tk.Entry(self.root, bd =0, textvariable=self.vel_y)
        label_vely.grid(row=6,column=2)
        label_vely_entry.grid(row=7,column=2)

        self.bounce = tk.BooleanVar(value=False)
        label_bounce = tk.Checkbutton(self.root, text="Bounce [yes/no]", variable=self.bounce)
        label_bounce.grid(row=8,column=2)

    def make_obstacle(self, event):

        obstacle = {}
        clicked_pos = [event.x, event.y]
        snapped_pos = self.snap_to_grid(clicked_pos)
        clicked_pixel = [click+pos for click,pos in zip(snapped_pos,self.position)]  # shift click with position of frame
        pos = self.pixel_to_world(clicked_pixel)
        obstacle['pos'] = pos
        if self.shape.get() == '':
            print 'Select a shape before placing an obstacle!'
            # self.obstacles.append()
        elif self.shape.get() == 'rectangle':
            if (self.width.get() <= 0 or self.height.get() <= 0):
                print 'Select a strictly positive width and height for the rectangle first'
            elif (self.width.get()*self.meter_to_pixel >= self.frame_width):
                print 'Selected width is too big'
            elif (self.height.get()*self.meter_to_pixel >= self.frame_height):
                print 'Selected height is too big'
            else:
                obstacle_var = self.canvas.create_rectangle(snapped_pos[0]-self.width.get()*self.meter_to_pixel/2., snapped_pos[1]-self.height.get()*self.meter_to_pixel/2.,
                                             snapped_pos[0]+self.width.get()*self.meter_to_pixel/2., snapped_pos[1]+self.height.get()*self.meter_to_pixel/2.,
                                             fill="black")
                obstacle['shape'] = 'rectangle'
                obstacle['width'] = self.width.get()
                obstacle['height'] = self.height.get()
                obstacle['velocity'] = [self.vel_x.get(), self.vel_y.get()]
                obstacle['bounce'] = self.bounce.get()
                obstacle['variable'] = obstacle_var
                self.obstacles.append(obstacle)
                print 'Created obstacle: ', obstacle
        elif self.shape.get() == 'circle':
            if (self.radius.get() <= 0):
                print 'Select a strictly positive radius before making a circle'
            elif (self.radius.get()*self.meter_to_pixel >= (self.frame_width or self.frame_height)):
                print 'Selected radius is too big'
            else:
                obstacle_var = self.canvas.create_circle(snapped_pos[0], snapped_pos[1], self.radius.get()*self.meter_to_pixel, fill="black")
                obstacle['shape'] = 'circle'
                obstacle['radius'] = self.radius.get()
                obstacle['velocity'] = [self.vel_x.get(), self.vel_y.get()]
                obstacle['bounce'] = self.bounce.get()
                obstacle['variable'] = obstacle_var
                self.obstacles.append(obstacle)
                print 'Created obstacle: ', obstacle
        # return self.obstacles

    def remove_last_obstacle(self):
        # when clicking the remove button, this removes
        # the obstacle which was created the last
        # erase from gui
        if self.obstacles:
            # get all ids of obstacles drawn on canvas
            ids = self.canvas.find_all()
            # delete the last id, corresponding to the last obstacle
            self.canvas.delete(ids[-1])
            # remove obstacle from list
            del self.obstacles[-1]

    def snap_to_grid(self, point):
        # Snap the user clicked point to a grid point, since obstacles can only
        # be placed on grid points
        snapped = [0,0]
        snapped[0] = int(self.cell_width * round(float(point[0])/self.cell_width))
        snapped[1] = int(self.cell_height * round(float(point[1])/self.cell_height))
        return snapped

    def get_position(self, event):
        clicked = [event.x,event.y]
        clicked = self.pixel_to_world(clicked)
        # self.clickedPos.set('['+str(clicked[0])+','+str(clicked[1])+']')
        print 'You clicked on: ', clicked
        self.clicked_positions.append(clicked)
        if (len(self.clicked_positions) > 2):
            self.clicked_positions[1] = self.clicked_positions[2]  # second last = last
            self.clicked_positions=self.clicked_positions[:2]  # remove last
            print 'You clicked more than two times, the last click replaced the previous one'

    def build_environment(self):
        # only build environment and shut down GUI if start and goal positions are clicked
        if len(self.clicked_positions) == 2:
            # make border
            self.environment = Environment(room={'shape': Rectangle(width = self.frame_width/self.meter_to_pixel,
                                                                    height = self.frame_height/self.meter_to_pixel),
                                                 'position':[(self.position[0]+self.frame_width/2.)/self.meter_to_pixel,
                                                             (self.position[1]+self.frame_height/2.)/self.meter_to_pixel]})                
            for obstacle in self.obstacles:
                if obstacle['shape'] == 'rectangle':
                    rectangle = Rectangle(width=obstacle['width'],height=obstacle['height'])
                    pos = obstacle['pos']
                    trajectory = {'velocity': {'time': [0.], 'values': [obstacle['velocity']]}}
                    simulation = {'trajectories': trajectory}
                    self.environment.add_obstacle(Obstacle({'position': pos}, shape=rectangle, simulation=simulation, options={'bounce': obstacle['bounce']}))
                elif obstacle['shape'] == 'circle':
                    circle = Circle(radius=obstacle['radius'])
                    pos = obstacle['pos']
                    trajectory = {'velocity': {'time': [0.], 'values': [obstacle['velocity']]}}
                    simulation = {'trajectories': trajectory}
                    self.environment.add_obstacle(Obstacle({'position': pos}, shape=circle, simulation=simulation, options={'bounce': obstacle['bounce']}))
                else:
                    raise ValueError('For now only rectangles and circles are supported, you selected a ' + obstacle['shape'])
            
            # if save environment is checked, save environment
            if self.save_env.get():
                self.save_environment()

            # close window
            self.destroy()
            self.root.destroy()
        else:
            print 'Please right-click on the start and goal position first'

    def save_environment(self):
        environment = {}
        environment['position'] = [0,0]
        environment['position'][0] = self.position[0]/self.meter_to_pixel
        environment['position'][1] = self.position[1]/self.meter_to_pixel
        environment['width'] = self.frame_width/self.meter_to_pixel
        environment['height'] = self.frame_height/self.meter_to_pixel
        env_to_save = [environment, self.obstacles, self.clicked_positions]
        with open('environment.pickle', 'wb') as handle:
            pickle.dump(env_to_save, handle, protocol=pickle.HIGHEST_PROTOCOL)

    def load_environment(self):
        # first remove all obstacles which are already present
        for obstacle in self.obstacles:
            self.canvas.delete(obstacle['variable'])
        with open('environment.pickle', 'rb') as handle:
            saved_env = pickle.load(handle)
        env = saved_env[0]
        self.position = env['position']*self.meter_to_pixel
        self.frame_width = env['width']*self.meter_to_pixel
        self.frame_height = env['height']*self.meter_to_pixel

        self.obstacles = saved_env[1]
        for obs in self.obstacles:
            # obstacle position is saved in world coordinates, convert to pixels to plot
            obs_pos = self.world_to_pixel(obs['pos'])
            obs_pos = self.snap_to_grid(obs_pos)
            if obs['shape'] == 'rectangle':
                self.canvas.create_rectangle(obs_pos[0]-obs['width']*self.meter_to_pixel/2., obs_pos[1]-obs['height']*self.meter_to_pixel/2.,
                                             obs_pos[0]+obs['width']*self.meter_to_pixel/2., obs_pos[1]+obs['height']*self.meter_to_pixel/2.,
                                             fill="black")
            elif obs['shape'] == 'circle':
                self.canvas.create_circle(obs_pos[0], obs_pos[1], obs['radius']*self.meter_to_pixel, fill="black")
        
        self.clicked_positions = saved_env[2]

    def get_environment(self):
        return self.environment

    def get_clicked_positions(self):
        return self.clicked_positions

    def _create_circle(self, x, y, r, **kwargs):
        return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)
    tk.Canvas.create_circle = _create_circle

    def pixel_to_world(self, pixel):
        # pixel min value ([0,0]) = top left
        # pixel max value = bottom right
        # convert this axis frame to the world axis,
        # i.e. min value = bottom left, max value = top right

        vmin = self.position[1]
        vmax = self.position[1] + self.frame_height
        # umin = self.position[0]
        # umax = self.frame_width
        # xmin = self.position[0]/self.meter_to_pixel
        # xmax = self.frame_width/self.meter_to_pixel
        # ymin = self.position[1]/self.meter_to_pixel
        # ymax = self.frame_height/self.meter_to_pixel
        u,v = pixel
        u,v = float(u), float(v)
        x = u/self.meter_to_pixel
        y = (vmax-v)/self.meter_to_pixel + vmin/self.meter_to_pixel
        return [x,y]

    def world_to_pixel(self, world):
        # convert world coordinate frame to pixel frame
        # = invert y-axis and shift

        vmin = self.position[1]
        vmax = self.position[1] + self.frame_height

        x,y = world
        x,y = float(x), float(y)
        u = x*self.meter_to_pixel
        v = -y*self.meter_to_pixel + vmin + vmax
        return [u,v]