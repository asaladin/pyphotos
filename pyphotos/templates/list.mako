<%inherit file="base.mako" />

<a href="addphoto">Ajouter une photo</a>
<a href="/createticket/${albumname}">Inviter quelqu'un</a>


liste des photos de l'album ${albumname}: <br />

%for p in photos:
<a href="${p['url']}"> 
    <img src="/thumbnail?filename=${p['filename']}" />  ${p['filename']} 
</a>  <br />    
%endfor