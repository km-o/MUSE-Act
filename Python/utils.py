# バンドパワーの計算処理などはbci_workshop_toolsのコードを使用

import numpy as np
from scipy.signal import butter, lfilter, lfilter_zi

import tensorflow as tf

NOTCH_B, NOTCH_A = butter(4, np.array([55, 65])/(256/2), btype='bandstop')

def epoch(data, samples_epoch, samples_overlap=0):
    """Extract epochs from a time series.
    Given a 2D array of the shape [n_samples, n_channels]
    Creates a 3D array of the shape [wlength_samples, n_channels, n_epochs]
    Args:
        data (numpy.ndarray or list of lists): data [n_samples, n_channels]
        samples_epoch (int): window length in samples
        samples_overlap (int): Overlap between windows in samples
    Returns:
        (numpy.ndarray): epoched data of shape
    """

    if isinstance(data, list):
        data = np.array(data)

    n_samples, n_channels = data.shape

    samples_shift = samples_epoch - samples_overlap

    n_epochs = int(
        np.floor((n_samples - samples_epoch) / float(samples_shift)) + 1)

    # Markers indicate where the epoch starts, and the epoch contains samples_epoch rows
    markers = np.asarray(range(0, n_epochs + 1)) * samples_shift
    markers = markers.astype(int)

    # Divide data in epochs
    epochs = np.zeros((samples_epoch, n_channels, n_epochs))

    for i in range(0, n_epochs):
        epochs[:, :, i] = data[markers[i]:markers[i] + samples_epoch, :]

    return epochs


def compute_feature_vector(eegdata, fs):
    """Extract the features from the EEG.
    Args:
        eegdata (numpy.ndarray): array of dimension [number of samples,
                number of channels]
        fs (float): sampling frequency of eegdata
    Returns:
        (numpy.ndarray): feature matrix of shape [number of feature points,
            number of different features]
    """
    # 1. Compute the PSD
    winSampleLength, nbCh = eegdata.shape

    # Apply Hamming window
    w = np.hamming(winSampleLength)
    dataWinCentered = eegdata - np.mean(eegdata, axis=0)  # Remove offset
    dataWinCenteredHam = (dataWinCentered.T*w).T

    NFFT = nextpow2(winSampleLength)
    Y = np.fft.fft(dataWinCenteredHam, n=NFFT, axis=0)/winSampleLength
    PSD = 2*np.abs(Y[0:int(NFFT/2), :])
    f = fs/2*np.linspace(0, 1, int(NFFT/2))

    # SPECTRAL FEATURES
    # Average of band powers
    # Delta <4
    ind_delta, = np.where(f < 4)
    meanDelta = np.mean(PSD[ind_delta, :], axis=0)
    # Theta 4-8
    ind_theta, = np.where((f >= 4) & (f <= 8))
    meanTheta = np.mean(PSD[ind_theta, :], axis=0)
    # Alpha 8-12
    ind_alpha, = np.where((f >= 8) & (f <= 12))
    meanAlpha = np.mean(PSD[ind_alpha, :], axis=0)
    # Beta 12-30
    ind_beta, = np.where((f >= 12) & (f < 30))
    meanBeta = np.mean(PSD[ind_beta, :], axis=0)

    feature_vector = np.concatenate((meanDelta, meanTheta, meanAlpha,
                                     meanBeta), axis=0)

    feature_vector = np.log10(feature_vector)

    return feature_vector


def nextpow2(i):
    """
    Find the next power of 2 for number i
    """
    n = 1
    while n < i:
        n *= 2
    return n


def compute_feature_matrix(epochs, fs):
    """
    Call compute_feature_vector for each EEG epoch
    """
    n_epochs = epochs.shape[2]

    for i_epoch in range(n_epochs):
        if i_epoch == 0:
            feat = compute_feature_vector(epochs[:, :, i_epoch], fs).T
            # Initialize feature_matrix
            feature_matrix = np.zeros((n_epochs, feat.shape[0]))

        feature_matrix[i_epoch, :] = compute_feature_vector(
            epochs[:, :, i_epoch], fs).T

    return feature_matrix


def get_feature_names(ch_names):
    """Generate the name of the features.
    Args:
        ch_names (list): electrode names
    Returns:
        (list): feature names
    """
    bands = ['delta', 'theta', 'alpha', 'beta']

    feat_names = []
    for band in bands:
        for ch in range(len(ch_names)):
            feat_names.append(band + '-' + ch_names[ch])

    return feat_names


def update_buffer(data_buffer, new_data, notch=False, filter_state=None):
    """
    Concatenates "new_data" into "data_buffer", and returns an array with
    the same size as "data_buffer"
    """
    if new_data.ndim == 1:
        new_data = new_data.reshape(-1, data_buffer.shape[1])

    if notch:
        if filter_state is None:
            filter_state = np.tile(lfilter_zi(NOTCH_B, NOTCH_A),
                                   (data_buffer.shape[1], 1)).T
        new_data, filter_state = lfilter(NOTCH_B, NOTCH_A, new_data, axis=0,
                                         zi=filter_state)

    new_buffer = np.concatenate((data_buffer, new_data), axis=0)
    new_buffer = new_buffer[new_data.shape[0]:, :]

    return new_buffer, filter_state


def get_last_data(data_buffer, newest_samples):
    """
    Obtains from "buffer_array" the "newest samples" (N rows from the
    bottom of the buffer)
    """
    new_buffer = data_buffer[(data_buffer.shape[0] - newest_samples):, :]

    return new_buffer


# Dropout層を入れても良いかもしれない
def build_model(shape):
  model = tf.keras.Sequential()
  model.add(tf.keras.Input(shape=shape))
  model.add(tf.keras.layers.Lambda(
      lambda x: tf.expand_dims(x, axis=2)))
  model.add(tf.keras.layers.GRU(256, return_sequences=True))
  # model.add(tf.keras.layers.BatchNormalization())
  model.add(tf.keras.layers.Flatten())
  model.add(tf.keras.layers.Dense(2, activation='softmax'))
  return model


def train(ft0, ft1):
  cl0 = np.zeros((ft0.shape[0], 1))
  cl1 = np.ones((ft1.shape[0], 1))

  ft = np.concatenate((ft0, ft1), axis=0)
  y = np.concatenate((cl0, cl1), axis=0)

  mu_ft = np.mean(ft, axis=0)
  std_ft = np.std(ft, axis=0)

  x = (ft - mu_ft) / std_ft

  model = build_model((ft.shape[1], ))
  # Compile model
  model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
  )

  history = model.fit(
    x,
    y,
    validation_split=0.2,
    batch_size=32,
    epochs=50,
    #callbacks=[
    #  tf.keras.callbacks.EarlyStopping(
    #    monitor='val_loss',
    #    patience=5,
    #    restore_best_weights=True
    #  )
    #]
  )

  return model, mu_ft, std_ft, history


def predict(model, feature_vector, mu_ft, std_ft):
    # Normalize feature_vector
    x = (feature_vector - mu_ft) / std_ft
    y_hat = model.predict(x)

    return y_hat

# テスト用
if __name__ == "__main__":
  model = build_model(shape=(16,))
  print(model.summary())
