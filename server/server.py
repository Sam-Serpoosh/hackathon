__author__ = 'rxue'
import csv, time, json
from flask import Flask, request
from cross_domain import crossdomain
from id_generator import IdGenerator
from user_finder import UserFinder

REG_FILE_PATH = "/Users/saserpoosh/projects/hackathon/app/data/registration_info.csv"
REG_INFO_FIELDS = ["id", "firstName", "lastName", "age", "weight", "height", "sex", "email", "image_url"]
REG_HEADER = ",".join(REG_INFO_FIELDS) + "\n"

app = Flask(__name__)
app.debug = True

tripData = []

@app.route("/")
def hello():
    return "Hello World"

@app.route("/count", methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_count():
  query = getQueryObject(request.args)
  range_query = getRangeQueryObject(request.args)
  print query
  return json.dumps(len(list(filter_data(query, range_query))))

@app.route("/data", methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def get_data():
  query = getQueryObject(request.args)
  range_query = getRangeQueryObject(request.args)
  print query
  return json.dumps(list(filter_data(query, range_query)))

# GET a user based on id

@app.route("/users", methods=["GET", "OPTIONS"])
@crossdomain(origin="*")
def get_user():
  query = getQueryObject(request.args)
  user_id = int(query["id"])
  user_finder = UserFinder(REG_FILE_PATH)
  user_info = user_finder.find_user_by_id(user_id)
  return json.dumps(user_info)

# Register a new user

@app.route("/register/", methods=["POST", "OPTIONS"])
def register():
  reg_info = get_registration_info(request.form)
  user_id = save_reg_info(reg_info)
  return json.dumps({ "message": "Registered wiht id: " + str(user_id), "code": "200" })

def get_registration_info(request_form):
  reg_info = dict()
  firstName, lastName, age = "firstName", "lastName", "age"
  weight, height, sex, email, image_url = "weight", "height", "sex", "email", "image_url"
  reg_info[firstName] = request_form[firstName]
  reg_info[lastName] = request_form[lastName]
  reg_info[age] = request_form[age]
  reg_info[weight] = request_form[weight]
  reg_info[height] = request_form[height]
  reg_info[sex] = request_form[sex]
  reg_info[email] = request_form[email]
  reg_info[image_url] = request_form[image_url]

  return reg_info

def save_reg_info(reg_info):
  write_header_if_not_there()
  reg_info_csv = convert_to_csv(reg_info, REG_INFO_FIELDS)
  f = open(REG_FILE_PATH, "a")
  f.write(str(reg_info_csv))
  f.close()
  user_info = reg_info_csv.split(",")
  user_id = int(user_info[0])
  return user_id


def convert_to_csv(info_dict, keys):
  user_id = IdGenerator(REG_FILE_PATH).generate_id()
  info_dict["id"] = user_id
  csv_reg_info = ""
  for key in keys:
    csv_reg_info += str(info_dict[key]) + ","
  return csv_reg_info[:-1] + "\n"

def write_header_if_not_there():
  try:
    f = open(REG_FILE_PATH, "r")
    f.readline()
    f.close()
  except IOError:
    f = open(REG_FILE_PATH, "w")
    f.write(REG_HEADER)
    f.close()

# End of Registering a new user

# Utility Methods

def getQueryObject(args):
  query = dict()
  for key in ["trip_id", "bikeid", "from_station_id", "to_station_id",
      "starthour", "endhour", "id"]:
    if key in args:
      query[key] = int(args.get(key))
  for key in ["usertype", "gender", "birthday"]:
    if key in args:
      query[key] = args.get(key)
  return query


def getRangeQueryObject(args):
  # expected: int(20131231)
  query = dict()
  for key in ["start_before", "end_before", "start_after", "end_after", "duration_smaller", "duration_larger"]:
    if key in args:
      query[key] = int(args.get(key))
  return query


def json_matches(jsonObejct, json_query):
    if len(json_query) == 0:
        return True
    for key in json_query:
        if not key in jsonObejct or jsonObejct[key] != json_query[key]:
            return False
    return True


def range_matches(jsonObject, range_query):
    if len(range_query) == 0:
        return True
    if "start_before" in range_query and jsonObject["startdate"] > range_query["start_before"]:
        return False
    if "end_before" in range_query and jsonObject["enddate"] > range_query["end_before"]:
        return False
    if "start_after" in range_query and jsonObject["startdate"] < range_query["start_after"]:
        return False
    if "end_after" in range_query and jsonObject["startdate"] < range_query["end_after"]:
        return False
    if "duration_smaller" in range_query and jsonObject["tripduration"] > range_query["duration_smaller"]:
        return False
    if "duration_larger" in range_query and jsonObject["tripduration"] < range_query["duration_larger"]:
        return False
    return True


def filter_data(query, time_query):
  for item in tripData:
    if json_matches(item, query) and range_matches(item, time_query):
      yield item

def load_trip_data():
    print "Hello"
    with open('rawdata/Divvy_Trips_2013.csv', 'rU') as csvIn:
        csvreader = csv.reader(csvIn)
        print csvIn.next().split(',')
        count = 0
        for row in csvreader:
            tripData.append({
                'trip_id': int(row[0]),
                'starttime': row[1],
                'stoptime': row[2],
                'bikeid': int(row[3]),
                'tripduration': int(row[4]),
                'from_station_id': int(row[5]),
                'from_station_name': row[6],
                'to_station_id': int(row[7]),
                'to_station_name': row[8],
                'usertype': row[9],
                'gender': row[10],
                'birthday': row[11],
                'starthour': int(row[1][11:13]),
                'endhour': int(row[2][11:13]),
                'startdate': int(row[1][0:4] + row[1][5:7] + row[1][8:10]),
                'enddate': int(row[2][0:4] + row[2][5:7] + row[2][8:10])
            })
            count += 1
            if count % 7597 == 0:
                print str(count / 7597) + "%"
    print "Data Loaded: " + str(len(tripData)) + " rows"


if __name__ == "__main__":
    load_trip_data()
    app.run()
