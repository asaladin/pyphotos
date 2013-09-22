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

      .photocontainer {
          margin-bottom: 15px;

       }

     .albumcontainer {

         display: inline-block;
         margin-bottom:30px;
         margin-right: 40px;
         width: 250px;
      }

     .albumcontainer:hover {
        background-color: #ccc;
        
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
            %if request.user is not None:
                <p class="navbar-text pull-right">Logged in as <a href="#">${request.user.username}</a> | <a href='/logout' id='signout'> logout </a> </p>
            %else: 
               <p class="navbar-text pull-right"><a id='signin' href="#" >Log in </a></p> 
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
                    %if request.user is not None:
                     <li><a href='/newalbum'>Create an album</a></li>
                    %endif
                     <li class="nav-header">Your albums</li>
                     %if request.user is not None:
                         %for a in request.user.albums[:5]:
                             <li><a href="/album/${a.name}/list">${a.name}</a></li>
                         %endfor
                     %endif
                 </ul>
             </div><!--/.well -->
         </div><!--/span-->



         <div class='span9'>
           ${next.body()}
         </div>

<script type="text/javascript" src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
<script src="https://login.persona.org/include.js" type="text/javascript"></script>
<script type="text/javascript">${request.persona_js}</script>



</body>

</html>
