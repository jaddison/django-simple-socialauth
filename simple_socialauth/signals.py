from django import dispatch

login = dispatch.Signal(providing_args=["request", "account", "user_info", "created"])
connect = dispatch.Signal(providing_args=["request", "account", "user_info", "created"])
