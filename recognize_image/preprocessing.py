import tensorflow as tf
import cv2
import numpy as np

from PIL import ImageFont
from PIL import ImageDraw

from midiutil.MidiFile import MIDIFile
from midiutil import MIDIFile

import os


def sparse_tensor_to_strs(sparse_tensor):
    indices = sparse_tensor[0][0]
    values = sparse_tensor[0][1]
    dense_shape = sparse_tensor[0][2]
    strs = [[] for i in range(dense_shape[0])]
    string = []
    ptr = 0
    b = 0
    for idx in range(len(indices)):
        if indices[idx][0] != b:
            strs[b] = string
            string = []
            b = indices[idx][0]
        string.append(values[ptr])
        ptr = ptr + 1
    strs[b] = string
    return strs


def normalize(image):
    return (255.0 - image) / 255.0


def resize(image, height):
    width = int(float(height * image.shape[1]) / image.shape[0])
    sample_img = cv2.resize(image, (width, height))
    return sample_img


def predict(image):
    current_directory = os.path.join(os.getcwd(), "recognize_image")
    model = os.path.join(current_directory, "model", "semantic_model.meta")

    tf.compat.v1.disable_eager_execution()
    sess = tf.compat.v1.InteractiveSession()
    # Restore weights
    saver = tf.compat.v1.train.import_meta_graph(model)
    saver.restore(sess, model[:-5])
    graph = tf.compat.v1.get_default_graph()
    with graph.as_default():
        tf.compat.v1.get_collection_ref("model_variables").clear()
    # access model
    input = graph.get_tensor_by_name("model_input:0")
    seq_len = graph.get_tensor_by_name("seq_lengths:0")
    rnn_keep_prob = graph.get_tensor_by_name("keep_prob:0")
    height_tensor = graph.get_tensor_by_name("input_height:0")
    width_reduction_tensor = graph.get_tensor_by_name("width_reduction:0")
    logits = tf.compat.v1.get_collection("logits")[0]
    # Constants that are saved inside the model itself
    WIDTH_REDUCTION, HEIGHT = sess.run([width_reduction_tensor, height_tensor])
    decoded, _ = tf.nn.ctc_greedy_decoder(logits, seq_len)

    voc_file = "vocabulary_semantic.txt"
    # Read the dictionary
    dict_file = open(os.path.join(current_directory, voc_file), "r")

    dict_list = dict_file.read().splitlines()
    int2word = dict()
    for word in dict_list:
        word_idx = len(int2word)
        int2word[word_idx] = word
        dict_file.close()

    image = resize(image, HEIGHT)
    image = normalize(image)
    image = np.asarray(image).reshape(1, image.shape[0], image.shape[1], 1)
    seq_lengths = [image.shape[2] / WIDTH_REDUCTION]
    prediction = sess.run(
        decoded,
        feed_dict={
            input: image,
            seq_len: seq_lengths,
            rnn_keep_prob: 1.0,
        },
    )

    str_predictions = sparse_tensor_to_strs(prediction)
    array_of_notes = []
    for w in str_predictions[0]:
        array_of_notes.append(int2word[w])
    notes = []
    for i in array_of_notes:
        if i[0:5] == "note-":
            if not i[6].isdigit():
                notes.append(i[5:])
            else:
                notes.append(i[5:])
    return notes


def sound_midi(notes):
    # Define note duration values
    duration_dict = {
        "whole": 4.0,
        "whole.": 6.0,
        "double": 8.0,
        "half": 2.0,
        "half.": 3.0,
        "quarter": 1.0,
        "quarter.": 1.5,
        "eighth": 0.5,
        "eighth.": 0.75,
        "sixteenth": 0.25,
        "sixteenth.": 0.375,
        "thirty": 0.125,
        "32nd": 0.125,
        "64th": 0.0625,
        "128th": 0.03125,
    }

    # Set some MIDI parameters
    BPM = 60
    NUM_TICKS_PER_BEAT = 480

    # Create a MIDI file object
    midifile = MIDIFile(1)

    # Add a track to the MIDI file
    track = 0
    midifile.addTrackName(track, time=0, trackName="Sheet Music Track")
    midifile.addTempo(track, time=0, tempo=int(400 * BPM))

    time = 0
    channel = 0
    for note_str in notes:
        note_parts = note_str.split("_")
        pitch_name = note_parts[0]
        duration_name = note_parts[1]

        # Convert the note name to MIDI pitch value
        pitch_classes = [
            "C",
            "C#",
            "D",
            "D#",
            "E",
            "F",
            "F#",
            "G",
            "G#",
            "A",
            "A#",
            "B",
        ]
        pitch_num = pitch_classes.index(pitch_name[0])

        # Calculate the MIDI note number for the given note name
        if pitch_name[-1].isdigit():
            note_pitch = int(pitch_name[-1]) + (int(pitch_num) + 1) * 12
        else:
            note_pitch = (int(pitch_name[1]) + 1) * 12

        # Get the duration in ticks
        note_duration = duration_dict[duration_name]
        duration_ticks = int(note_duration * NUM_TICKS_PER_BEAT)

        # Add the note to the MIDI file
        midifile.addNote(
            track=track,
            channel=channel,
            pitch=note_pitch,
            time=time,
            duration=duration_ticks,
            volume=127,
        )

        # Increment the time counter
        time += duration_ticks
    return midifile
