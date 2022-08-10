from asyncore import loop
from pythonosc import dispatcher, osc_server, udp_client
import utils
import numpy as np  # Module that simplifies computations on matrices
from pylsl import StreamInlet, resolve_byprop  # Module to receive EEG data

import asyncio

IP_ADDRESS = "127.0.0.1"
UNITY_OSC_CLIENT_PORT = 5001
PYTHON_OSC_CLIENT_PORT = 5002

def calibration():
  print(f"Start calibraiton...")
  client.send_message("/musePy/calibration", "start")
  """ 1. CONNECT TO EEG STREAM """

  # Search for active LSL stream
  print('Looking for an EEG stream...')
  streams = resolve_byprop('type', 'EEG', timeout=2)
  if len(streams) == 0:
      raise RuntimeError('Can\'t find EEG stream.')

  # Set active EEG stream to inlet and apply time correction
  print("Start acquiring data")
  inlet = StreamInlet(streams[0], max_chunklen=12)
  eeg_time_correction = inlet.time_correction()

  # Get the stream info, description, sampling frequency, number of channels
  info = inlet.info()
  description = info.desc()
  fs = int(info.nominal_srate())
  n_channels = info.channel_count()

  # Get names of all channels
  ch = description.child('channels').first_child()
  ch_names = [ch.child_value('label')]
  for i in range(1, n_channels):
      ch = ch.next_sibling()
      ch_names.append(ch.child_value('label'))

  """ 2. SET EXPERIMENTAL PARAMETERS """

  # Length of the EEG data buffer (in seconds)
  # This buffer will hold last n seconds of data and be used for calculations
  buffer_length = 15

  # Length of the epochs used to compute the FFT (in seconds)
  epoch_length = 1

  # Amount of overlap between two consecutive epochs (in seconds)
  overlap_length = 0.8

  # Amount to 'shift' the start of each next consecutive epoch
  shift_length = epoch_length - overlap_length

  # Index of the channel (electrode) to be used
  # 0 = left ear, 1 = left forehead, 2 = right forehead, 3 = right ear
  index_channel = [0, 1, 2, 3]
  # Name of our channel for plotting purposes
  ch_names = [ch_names[i] for i in index_channel]
  n_channels = len(index_channel)

  # Get names of features
  # ex. ['delta - CH1', 'pwr-theta - CH1', 'pwr-alpha - CH1',...]
  feature_names = utils.get_feature_names(ch_names)

  # Number of seconds to collect training data for (one class)
  training_length = 30

  """ 3. RECORD TRAINING DATA """

  client.send_message("/musePy/calibration", "right")
  eeg_data0, timestamps0 = inlet.pull_chunk(
      timeout=training_length+1, max_samples=fs * training_length)
  eeg_data0 = np.array(eeg_data0)[:, index_channel]

  client.send_message("/musePy/calibration", "left")
  eeg_data1, timestamps1 = inlet.pull_chunk(
      timeout=training_length+1, max_samples=fs * training_length)
  eeg_data1 = np.array(eeg_data1)[:, index_channel]

  # Divide data into epochs
  eeg_epochs0 = utils.epoch(eeg_data0, epoch_length * fs,
                            overlap_length * fs)
  eeg_epochs1 = utils.epoch(eeg_data1, epoch_length * fs,
                            overlap_length * fs)

  client.send_message("/musePy/calibration", "end")
  """ 4. COMPUTE FEATURES AND TRAIN CLASSIFIER """

  feat_matrix0 = utils.compute_feature_matrix(eeg_epochs0, fs)
  feat_matrix1 = utils.compute_feature_matrix(eeg_epochs1, fs)

  model, mu_ft, std_ft, history = utils.train(feat_matrix0, feat_matrix1)
  
  """ 5. USE THE CLASSIFIER IN REAL-TIME"""

  # Initialize the buffers for storing raw EEG and decisions
  eeg_buffer = np.zeros((int(fs * buffer_length), n_channels))
  filter_state = None  # for use with the notch filter

  # The try/except structure allows to quit the while loop by aborting the
  # script with <Ctrl-C>
  print('Press Ctrl-C in the console to break the while loop.')
  client.send_message("/musePy/calibration", "predStart")
  global predicting
  predicting = True
  try:
      while predicting:
          """ 3.1 ACQUIRE DATA """
          # Obtain EEG data from the LSL stream
          eeg_data, timestamp = inlet.pull_chunk(
              timeout=1, max_samples=int(shift_length * fs))

          # Only keep the channel we're interested in
          ch_data = np.array(eeg_data)[:, index_channel]

          # Update EEG buffer
          eeg_buffer, filter_state = utils.update_buffer(
              eeg_buffer, ch_data, notch=True,
              filter_state=filter_state)

          """ 3.2 COMPUTE FEATURES AND CLASSIFY """
          # Get newest samples from the buffer
          data_epoch = utils.get_last_data(eeg_buffer,
                                          epoch_length * fs)

          # Compute features
          feat_vector = utils.compute_feature_vector(data_epoch, fs)
          y_hat = utils.predict(model,
                                feat_vector.reshape(1, -1), mu_ft,
                                std_ft)
          client.send_message("/musePy/predict", [float(y_hat[0][0]), float(y_hat[0][1])])
  except KeyboardInterrupt:
      print('Closed!')
      predicting = False
      client.send_message("/musePy/calibration", "predEnd")

# asyncioよくわからないのでとりあえず30秒で強制終了
async def loop():
    for i in range(30):
        print(f"TO {i}/30")
        await asyncio.sleep(1)

async def run_server():
    server = osc_server.AsyncIOOSCUDPServer(
        (IP_ADDRESS, UNITY_OSC_CLIENT_PORT), dispatcher, asyncio.get_event_loop())
    transport, _ = await server.create_serve_endpoint()
    await loop()
    transport.close()
  
def muse_unity_handle(_, msg):
    if msg == "start":
        calibration()
    elif msg == "end":
        global predicting
        predicting = False
        print("predicting is False")

if __name__ == "__main__":

  predicting = False

  client = udp_client.SimpleUDPClient(IP_ADDRESS, PYTHON_OSC_CLIENT_PORT)

  dispatcher = dispatcher.Dispatcher()
  dispatcher.map("/museUnity", muse_unity_handle)

  asyncio.run(run_server())




