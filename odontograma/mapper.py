import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import json
import os

# --- CONFIGURATION ---
IMAGE_PATH = 'odontograma_default.png' # Make sure this matches your file name
OUTPUT_FILE = 'diente_fixtures.json'

# Standard ISO 3950 numbering for Adult and Child arches
TEETH_ORDER = [
    # Top Adult (Right to Left)
    18, 17, 16, 15, 14, 13, 12, 11, 21, 22, 23, 24, 25, 26, 27, 28,
    # Top Child
    55, 54, 53, 52, 51, 61, 62, 63, 64, 65,
    # Bottom Child
    85, 84, 83, 82, 81, 71, 72, 73, 74, 75,
    # Bottom Adult
    48, 47, 46, 45, 44, 43, 42, 41, 31, 32, 33, 34, 35, 36, 37, 38
]

class OdontogramaMapper:
    def __init__(self, image_path):
        if not os.path.exists(image_path):
            print(f"Error: Image {image_path} not found.")
            exit()
            
        self.img = plt.imread(image_path)
        self.fig, self.ax = plt.subplots(figsize=(15, 10))
        self.img_height, self.img_width, _ = self.img.shape
        
        self.current_idx = 0
        self.click_start = None
        self.results = []
        
        # Setup Plot
        self.ax.imshow(self.img)
        self.ax.set_title("ODONTOGRAMA MAPPER")
        self.status_text = self.ax.text(0, -20, "", fontsize=12, color='blue')
        
        # Connect events
        self.cid_press = self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        self.update_prompt()
        plt.show()

    def update_prompt(self):
        if self.current_idx < len(TEETH_ORDER):
            tooth_num = TEETH_ORDER[self.current_idx]
            msg = f"STEP {self.current_idx + 1}/{len(TEETH_ORDER)}: Draw Box for Tooth #{tooth_num}\nClick TOP-LEFT, then BOTTOM-RIGHT"
            self.status_text.set_text(msg)
            self.ax.set_title(f"MAPPING TOOTH: {tooth_num}")
            plt.draw()
        else:
            self.save_data()
            plt.close()

    def on_click(self, event):
        if event.inaxes != self.ax: return
        
        if self.current_idx >= len(TEETH_ORDER): return

        if self.click_start is None:
            # First click (Top-Left)
            self.click_start = (event.xdata, event.ydata)
            plt.plot(event.xdata, event.ydata, 'ro') # Mark point
            plt.draw()
        else:
            # Second click (Bottom-Right)
            x1, y1 = self.click_start
            x2, y2 = event.xdata, event.ydata
            
            # Calculate coordinates
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            
            # Draw visual confirmation box
            rect = Rectangle((x, y), w, h, linewidth=2, edgecolor='r', facecolor='none')
            self.ax.add_patch(rect)
            
            # --- CONVERT TO PERCENTAGE (0.0 - 1.0) ---
            # This makes it responsive for mobile!
            data = {
                "model": "core.diente", # Change 'core' to your app name
                "pk": TEETH_ORDER[self.current_idx], # Use tooth number as ID
                "fields": {
                    "numero": TEETH_ORDER[self.current_idx],
                    "hitbox_json": json.dumps({
                        "x": round(x / self.img_width, 4),
                        "y": round(y / self.img_height, 4),
                        "width": round(w / self.img_width, 4),
                        "height": round(h / self.img_height, 4)
                    })
                }
            }
            self.results.append(data)
            
            # Reset and move to next
            self.click_start = None
            self.current_idx += 1
            self.update_prompt()

    def save_data(self):
        print("Mapping Complete! Saving JSON...")
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(self.results, f, indent=4)
        print(f"Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    OdontogramaMapper('odontograma/images/odontograma_default.png')