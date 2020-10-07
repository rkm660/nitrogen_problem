import csv
from glob import glob
import math
from random import random, randint


def generate_sample_images(num_images, num_points):
    # list of num_images images, each containing a random number of between 1 and num_points points
    sample_images = [[(i, random(), random()) for i in range(randint(1, num_points))] for j in range(num_images)]

    for image_num, sample_image in enumerate(sample_images):
        with open('{}.csv'.format(image_num + 1), 'wb') as csv_file:
            file_writer = csv.writer(csv_file, delimiter=',')
            for point in sample_image:
                id_val, x, y = point
                file_writer.writerow([str(id_val), str(x), str(y)])

    
def read_sample_images():
    all_raw_image_data = {}
    all_csv_file_names = glob('*.csv')
    for file_name in all_csv_file_names:
        current_image_rows = []
        with open(file_name, 'rb') as f:
            file_reader = csv.reader(f)
            for row in file_reader:
                current_image_rows.append((int(row[0]),float(row[1]), float(row[2])))
        all_raw_image_data[file_name[:file_name.find('.')]] = current_image_rows
        
    return all_raw_image_data


def point_in_distance_range(point_pair_distance, target_magnitude, distance_error):
    return (point_pair_distance > (target_magnitude - distance_error)) and (point_pair_distance < (target_magnitude + distance_error))


def point_in_angle_range(point_pair_angle_radians, target_point_x, target_point_y, angle_delta):
    return (point_pair_angle_radians > (math.atan2(target_point_y, target_point_x) - angle_delta)) and (point_pair_angle_radians < (math.atan2(target_point_y, target_point_x) + angle_delta))


def is_point_eligible(point_x, point_y, target_point_x, target_point_y, distance_error, angle_delta):
    # TODO
    return False


def compute_probability_of_slice(all_raw_image_data, image_to_distance_angle_mapping, ring_radius, distance_error, angle_delta):

    points_in_range = []
    all_eligible_points = []

    target_point_x = ring_radius * math.cos(ring_radius)
    target_point_y = ring_radius * math.sin(ring_radius)
    target_magnitude = math.sqrt(target_point_x**2 + target_point_y**2)
    
    for image in image_to_distance_angle_mapping:
        for point_pair in image_to_distance_angle_mapping[image]:
            point_pair_distance, point_pair_angle_radians, point_pair_angle_degrees = image_to_distance_angle_mapping[image][point_pair]
            if point_in_distance_range(
                point_pair_distance,
                target_magnitude,
                distance_error
            ) and point_in_angle_range(
                point_pair_angle_radians,
                target_point_x,
                target_point_y,
                angle_delta
            ):
                points_in_range.append((image, point_pair))

    for image in all_raw_image_data:
        for point_tuple in all_raw_image_data[image]:
            id_val, point_x, point_y = point_tuple
            if is_point_eligible(point_x, point_y, target_point_x, target_point_y, distance_error, angle_delta):
                all_eligible_points.append((image, id_val))
    print(len(all_eligible_points))

    try:
        probability = float(len(points_in_range)) / len(all_eligible_points)
    except ZeroDivisionError:
        probability = 0.0                                          
    return probability

    
def construct_image_to_distance_angle_mapping(all_raw_image_data):
    all_image_to_distance_angle_mapping = {}
    for image_id in all_raw_image_data:
        current_distance_angle_data = {}
        current_raw_image_data = all_raw_image_data[image_id]
        for point_a in current_raw_image_data:
            for point_b in current_raw_image_data:
                a_id, a_x, a_y = str(point_a[0]), point_a[1], point_a[2]
                b_id, b_x, b_y = str(point_b[0]), point_b[1], point_b[2]

                if a_id != b_id:
      
                    distance_between_points = math.sqrt((b_x - a_x)**2 + (b_y - a_y)**2)
                    angle_formed_from_a_to_b_as_radians = math.atan2(b_y - a_y, b_x - a_x)
                    angle_formed_from_a_to_b_as_degrees = math.degrees(angle_formed_from_a_to_b_as_radians)
                    
                    current_distance_angle_data[a_id + '-' + b_id] = (distance_between_points,
                                                                      angle_formed_from_a_to_b_as_radians,
                                                                      angle_formed_from_a_to_b_as_degrees)
                    
        all_image_to_distance_angle_mapping[image_id] = current_distance_angle_data

    return all_image_to_distance_angle_mapping
                       

def construct_probability_matrix(distance_precision, distance_error, angle_error):

    # Read in all .csv files in current directory (see sample file)
    all_raw_image_data = read_sample_images()

    # Create map from <image_id> -> <point_a>-<point_b> -> to tuples of 1) distance between point, angle from a to b in radians, angle from a to b in degrees 
    image_to_distance_angle_mapping = construct_image_to_distance_angle_mapping(
        all_raw_image_data
    )

    # Create result map from 
    slice_to_probability_map = {}
    
    for ring_radius in range(1, 3, 1):
        for angle_delta in range(0, 360, angle_error):
            normalized_radius = float(ring_radius)/100
            current_slice_probability = compute_probability_of_slice(
                all_raw_image_data,
                image_to_distance_angle_mapping,
                normalized_radius,
                distance_error,
                angle_delta
            )
            slice_to_probability_map[str(normalized_radius) + '-' + str(angle_delta)] = current_slice_probability

    return slice_to_probability_map

    
result_probability_matrix = construct_probability_matrix(2, 1, 24)
 


