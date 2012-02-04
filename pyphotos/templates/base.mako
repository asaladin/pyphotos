<html>
<head>
<title>Photos</title>

</head>

<body>

<div class="flash"> 
<% flash = request.session.pop_flash()   %>
  %for message in flash:
    ${message} <br />
  %endfor
</div>

<div class="menu">

Hello ${username}

<ul>
<li><a href="/">main page</a></li>
<li><a href='/newalbum'>create an album</a></li>
</ul>
</div>

<div class="body">

   ${next.body()}

</div>

</body>

</html>
