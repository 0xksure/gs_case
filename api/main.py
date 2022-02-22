from datetime import datetime
import xarray
import datetime
import numpy as np

data = xarray.open_dataset("~/Documents/datasets/waves.nc")
some_date = datetime.date.fromisoformat("2019-01-01")
selected_time_data = data.sel(time="2019-01-01T00:00:00")
selected_location = selected_time_data.loc[dict(latitude=0.0, longitude=0.0)]
max_wave_height = selected_location["hmax"]
max_wave_height_2019 = np.max(np.nan_to_num(selected_time_data["hmax"].values))
print("1. max wave height (hmax) at coordinates (0.000, 0.000) on 2019-01-01: ", max_wave_height_2019)
