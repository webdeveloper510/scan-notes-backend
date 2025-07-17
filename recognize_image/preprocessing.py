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
    model_path = os.path.join(current_directory, "model", "semantic_model.meta")
    voc_file = os.path.join(current_directory, "vocabulary_semantic.txt")

    tf.compat.v1.disable_eager_execution()

    with tf.compat.v1.Session() as sess:
        saver = tf.compat.v1.train.import_meta_graph(model_path)
        try:
            saver.restore(sess, model_path[:-5])
        except Exception as e:
            print("Model restoration failed:", e)
            return []

        graph = tf.compat.v1.get_default_graph()
        input = graph.get_tensor_by_name("model_input:0")
        seq_len = graph.get_tensor_by_name("seq_lengths:0")
        rnn_keep_prob = graph.get_tensor_by_name("keep_prob:0")
        height_tensor = graph.get_tensor_by_name("input_height:0")
        width_reduction_tensor = graph.get_tensor_by_name("width_reduction:0")
        logits = tf.compat.v1.get_collection("logits")[0]

        WIDTH_REDUCTION, HEIGHT = sess.run([width_reduction_tensor, height_tensor])
        decoded, _ = tf.nn.ctc_greedy_decoder(logits, seq_len)

        with open(voc_file, "r") as f:
            dict_list = f.read().splitlines()
        int2word = {i: word for i, word in enumerate(dict_list)}

        image = resize(image, HEIGHT)
        image = normalize(image)
        image = np.asarray(image).reshape(1, image.shape[0], image.shape[1], 1)
        seq_lengths = [image.shape[2] // WIDTH_REDUCTION]

        prediction = sess.run(decoded, feed_dict={
            input: image,
            seq_len: seq_lengths,
            rnn_keep_prob: 1.0,
        })

        str_predictions = sparse_tensor_to_strs(prediction)
        notes = [int2word[w][5:] for w in str_predictions[0] if int2word[w].startswith("note-")]
        return notes


def sound_midi(notes):
    # Define note duration values in beats
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

    # MIDI setup
    BPM = 60
    NUM_TICKS_PER_BEAT = 480
    midifile = MIDIFile(1)
    track = 0
    channel = 0
    time = 0

    midifile.addTrackName(track, time=0, trackName="Sheet Music Track")
    midifile.addTempo(track, time=0, tempo=BPM)

    pitch_classes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    for note_str in notes:
        try:
            pitch_name, duration_name = note_str.split("_")
            # Extract pitch class and octave
            for pc in pitch_classes:
                if pitch_name.startswith(pc):
                    pitch_class = pc
                    octave = int(pitch_name[len(pc):])
                    break
            else:
                raise ValueError(f"Unknown pitch: {pitch_name}")

            pitch_num = pitch_classes.index(pitch_class)
            midi_pitch = 12 * (octave + 1) + pitch_num  # MIDI note number

            if duration_name not in duration_dict:
                raise ValueError(f"Unknown duration: {duration_name}")
            duration_beats = duration_dict[duration_name]
            duration_ticks = int(duration_beats * NUM_TICKS_PER_BEAT)

            midifile.addNote(
                track=track,
                channel=channel,
                pitch=midi_pitch,
                time=time,
                duration=duration_ticks,
                volume=127,
            )
            time += duration_beats  # Advance time in beats, not ticks
        except Exception as e:
            print(f"Skipping invalid note '{note_str}': {e}")

    return midifile
