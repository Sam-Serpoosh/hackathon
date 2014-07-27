class UserFinder:

  def __init__(self, filename):
    self.filename = filename

  def find_user_by_id(self, user_id):
    content_lines = self.read_file_lines()
    for line in content_lines:
      user_info = line.split(",")
      try:
        user_identification = int(user_info[0])
        if user_identification == user_id:
          return self.user_info_dict(user_info)
      except ValueError:
        pass
    return None

  def read_file_lines(self):
    f = open(self.filename, "r")
    lines = f.readlines()
    f.close()
    return lines

  def user_info_dict(self, user_info):
    return {
      "id": user_info[0],
      "firstName": user_info[1],
      "lastName": user_info[2],
      "age": user_info[3],
      "weight": user_info[4],
      "height": user_info[5],
      "gender": user_info[6],
      "email": user_info[7],
      "image_url": user_info[8]
    }

