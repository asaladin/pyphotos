<html>
<head>
<title>Photos</title>

<style type="text/css">
      body {
        padding-top: 60px;
        padding-bottom: 40px;
      }
      .sidebar-nav {
        padding: 9px 0;
      }
    </style>



<link href="/static/bootstrap.css" rel="stylesheet">
<script src="static/bootstrap.js"></script>
</head>

<body>




    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="/">PyPhotos</a>
          <div class="nav-collapse">
            <ul class="nav">
              <li><a href="/">Home</a></li>
            ##  <li><a href="#about">About</a></li>
            ##  <li><a href="#contact">Contact</a></li>
            </ul>
            %if username is not None:
                <p class="navbar-text pull-right">Logged in as <a href="#">${username}</a> | <a href='/logout'> logout </a> </p>
            %else: 
               <p class="navbar-text pull-right"><a href="/login">Log in </a></p> 
            %endif    
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>



<div class="container-fluid">

     <div class="flash"> 
        <% flash = request.session.pop_flash()   %>
        %for message in flash:
             ${message} <br />
        %endfor
     </div>

     <div class="row-fluid">

         <div class="span2">
             <div class="well sidebar-nav">
                 <ul class="nav nav-list">
                     <li class="nav-header">Sidebar</li>
    <!--             <li class="active"><a href="#">Link</a></li>-->
                     <li><a href='/newalbum'>Create an album</a></li>
                     <li class="nav-header">Your albums</li>
                     %for a in myalbums[:5]:
                         <li><a href="/album/${a['title']}/list">${a['title']}</a></li>
                     %endfor
                 </ul>
             </div><!--/.well -->
         </div><!--/span-->





         <div class="span10">
             <div class="hero-unit">
                <h1>Hello, world!</h1>
                <p>This is a template for a simple marketing or informational website. It includes a large callout called the hero unit and three supporting pieces of content. Use it as a starting point to create something more unique.</p>
                <p><a class="btn btn-primary btn-large">Learn more &raquo;</a></p>
             </div>
         




         <div class="row-fluid">
             <div class='span9'>
                  ${next.body()}
             </div>
         </div>




</body>

</html>
