from marshmallow import Schema, fields


class FileSchema(Schema):
	filename = fields.Str()


class MultiSegmentSchema(Schema):
	filename = fields.Nested(FileSchema)
	segment = fields.List(fields.Str())
	count = fields.List(fields.Int())


class SingleSegmentSchema(Schema):
	segment = fields.List(fields.Str())
	count = fields.List(fields.Int())
