from context import Instagram # pylint: disable=no-name-in-module

instagram = Instagram.withCredentials('username', 'password', 'path/to/cache/folder')
instagram.login()

instagram.like('1874597980243548658')
instagram.unlike('1874597980243548658')