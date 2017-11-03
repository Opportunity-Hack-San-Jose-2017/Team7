"""

"""


class UshahidiDataStructure:
    """
    Represents a data structure for Ushahidi platform
    """

    @classmethod
    def deserialize(cls, json: dict):
        """
        :param json:
        :return:
        """
        return cls(**json)

    def get_json(self):
        result = {}
        for key, value in self.__dict__.items():
            if key == 'misc_json_data':
                continue
            if value:
                result[key] = value
        return result


class Form(UshahidiDataStructure):
    """
    Sample response
    {"id": 1, 
    "url": "https://plato1.api.ushahidi.io/api/v3/forms/1", 
    "parent_id": None, 
    "name": "Basic Post", 
    "description": "Post with a location", 
    "color": None, 
    "type": "report", 
    "disabled": False, 
    "created": "2017-11-01T02:34:12+00:00", 
    "updated": "2017-11-01T23:36:06+00:00", 
    "hide_author": False, 
    "require_approval": True, 
    "everyone_can_create": True, 
    "can_create": [], 
    "tags": [{"id": 1, "url": "https://plato1.api.ushahidi.io/api/v3/tags/1"}], 
    "allowed_privileges": ["read", "create", "update", "delete", "search"]
    }
    
    """

    def __init__(self, id: int, url: str = None, parent_id: int = None, name: str = None, description: str = None,
                 color: str = None, type: str = None, **kwargs):
        self.id = id
        self.url = url
        self.parent_id = parent_id
        self.name = name
        self.description = description
        self.color = color
        self.type_ = type
        self.misc_json_data = kwargs

    def __repr__(self):
        return 'Ushahidi-ds-{}: id: {} ({})'.format(self.__class__.__name__, self.id, self.name)


class FormAttribute(UshahidiDataStructure):
    """
    Sample response
    {'id': 1,
    'url': 'https://plato1.api.ushahidi.io/api/v3/form_attributes/1',
    'key': 'location_default',
    'label': 'Location',
    'instructions': None,
    'input': 'location',
    'type': 'point',
    'required': False,
    'default': None,
    'priority': 0,
    'options': None,
    'cardinality': 1,
    'config': None,
    'form_stage_id': 1,
    'response_private': False,
    'allowed_privileges': ['read', 'create', 'update', 'delete', 'search']}

    """

    def __init__(self, id: int, url: str, key: str, label: str, type: str, input: str, required: bool,
                 default: str, instructions: str, **kwargs):
        self.id = id
        self.url = url
        self.key = key
        self.label = label
        self.input = input
        self.required = required
        self.default = default
        self.type_ = type
        self.misc_json_data = kwargs
        self.instructions = instructions
        self.__transform()

    def __repr__(self):
        return 'Ushahidi-ds-{}: id: {} ({})'.format(self.__class__.__name__, self.id, self.label)

    def __transform(self):
        """
        Porting from
        https://github.com/natmanning/platform-facebook-bot/blob/master/app/Services/PlatformApiService.php
        :return:
        """
        if self.default:
            # Do nothing if there is a default value
            return
        if self.type_ == 'media':
            self.label = 'image'
        elif self.type_ == 'point':
            self.label = 'location'


class Post(UshahidiDataStructure):
    """
    ### Post
        + id: 530 (number)
        + url: https://quakemap.api.ushahidi.io/api/v3/posts/530 (string)
        + parent (object, nullable)
            + id: 1
            + url: https://demo.api.ushahidi.io/api/v3/posts/1
        + title: Need help (required)
        + content: Asrang VDC of Gorkha hasn't received any help yet. Need relief efforts (required)
        + created: `2014-11-11T08:40:51+00:00`
        + updated: `2014-11-11T08:40:51+00:00`
        + form
            + id: 1
            + url: https://quakemap.api.ushahidi.io/api/v3/forms/1
        + user
            + id: 1
            + url: https://quakemap.api.ushahidi.io/api/v3/users/1
        + message
        + color: #2274B4 (string)
        + type: report (string)
        + slug: `chhokang-paro-village-upper-tsum-medical-ampamp-food-assistance-urgently-required-560b50a52fe02`
        + author_email: null
        + author_realname: null
        + status: published
        + locale: en_us
        + published_to (array)
        + completed_stages (array[number])
        + values (object) - Custom field values. Object keys map to Form Attribute key field
            + AttributeID1 (array[*])
                + Value 1
                + Value 2
            + AttributeID2 (array[*])
                + (object)
                    + lat: 2.456
                    + lon: 1.234
        + tags (array)
            + (object)
              + id: 1 (number)
              + url: https://quakemap.api.ushahidi.io/api/v3/tags/1 (string)
        + sets: 1, 2 (array[string])
        + source: SMS (string) - Original Message source ie. SMS, Twitter
        + contact: rjmackay (string) - Contact Identifier ie. SMS number, twitter handle
        + Include AllowedPrivileges

    """

    def __init__(self, title: str = None, content: str = None, id: int = None, url: str = None, form: any = None,
                 source: str = None,
                 contact: str = None, author_email: str = None,
                 author_realname: str = None, status: str = None, locale: str = 'en_us', values: any = None, **kwargs):
        self.title = title
        self.content = content
        self.id = id
        self.url = url
        self.form = form
        self.source = source
        self.contact = contact
        self.author_email = author_email
        self.author_realname = author_realname
        self.status = status
        self.locale = locale
        self.values = values
        self.misc_json_data = kwargs

    def set_form(self, form: Form):
        self.form = dict()
        self.form['id'] = form.id
        self.form['url'] = form.url

    def __repr__(self):
        return 'Ushahidi-ds-{}: id: {} ({})'.format(self.__class__.__name__, self.id, self.title)
