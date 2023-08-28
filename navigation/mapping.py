import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg


class Mapping:
    def __init__(self, start: int, grid: dict,
                 pause: float = 0.01, image=None):
        """Initialize mapping

        Parameters
        ----------
        start : int
            Identifier of start node
        grid : dict
            Grid map
        pause : float, Optional
            Pause time for animation, by default 0.01
        image: Union[str, Path], Optional
            Map .png image, by default None
        """
        self.start, self.grid = start, grid
        self.pause = pause
        self.image = image

        # Gradient for risk (green 0 to red 1)
        self.RISK_MARKERS = [
            "#10FF00", "#20FF00", "#30FF00", "#40FF00", "#50FF00", "#60FF00",
            "#70FF00", "#80FF00", "#90FF00", "#A0FF00", "#B0FF00", "#C0FF00",
            "#D0FF00", "#E0FF00", "#F0FF00", "#FFFF00", "#FFF000", "#FFE000",
            "#FFD000", "#FFC000", "#FFB000", "#FFA000", "#FF9000", "#FF8000",
            "#FF7000", "#FF6000", "#FF5000", "#FF4000", "#FF3000", "#FF2000",
            "#FF1000", "#FF0000",
        ]

    def animate(self, path, visited):
        fig, ax = plt.subplots(figsize=(4, 3), dpi=100)
        plt.xlim([0, self.grid['columns'] - 1])
        plt.ylim([0, self.grid['rows'] - 1])

        self._plot_image()
        self.create_map()
        # self._plot_visited(visited)
        self._plot_path(path)

        plt.show()
        return fig, ax

    def _plot_image(self):
        if self.image is None:
            return

        xlim = [0, self.grid['columns'] - 1]
        ylim = [0, self.grid['rows'] - 1]

        img = mpimg.imread(self.image)

        img = np.flipud(img)

        plt.imshow(img, extent=[xlim[0], xlim[1], ylim[0], ylim[1]],
                   aspect='auto')

    def _to_coordinate(self, node):
        return np.unravel_index(
            node, (self.grid['rows'], self.grid['columns']))

    def create_map(self):

        start_coord = self._to_coordinate(self.start)

        plt.plot(start_coord[1], start_coord[0], "rs")

        for zone in self.grid['safe_zones']:
            zone_coord = self._to_coordinate(zone)
            plt.plot(zone_coord[1], zone_coord[0], "gs")

        # Plot the internal non-traversable terrain as black
        for cell in self.grid['cells']:
            if len(cell['connections']) != 0:
                continue

            cell_coord = self._to_coordinate(cell['id'])

            plt.plot(cell_coord[1], cell_coord[0], "sk")

    def _plot_path(self, path, cl='r', flag=False):
        path_x = []
        path_y = []
        for cell in path:
            x, y = self._to_coordinate(cell)
            path_x.append(x)
            path_y.append(y)

        if not flag:
            plt.plot(path_y, path_x, linewidth='3', color='r')
        else:
            plt.plot(path_y, path_x, linewidth='3', color=cl)

        plt.pause(self.pause)

    def _plot_visited(self, visited, cl='gray'):
        if self.start in visited:
            visited.remove(self.start)

        for zone in self.grid['safe_zones']:
            if zone in visited:
                visited.remove(zone)

        count = 0

        for node in visited:
            y, x = self._to_coordinate(node)

            count += 1
            plt.plot(x, y, color=cl, marker='o')
            plt.gcf().canvas.mpl_connect(
                'key_release_event',
                lambda event: [exit(0) if event.key == 'escape' else None])

            if count < len(visited) / 3:
                length = 20
            elif count < len(visited) * 2 / 3:
                length = 30
            else:
                length = 40

            if count % length == 0:
                plt.pause(0.001)
            plt.pause(self.pause)
