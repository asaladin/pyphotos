<%inherit file="base.mako" />

<a href="addphoto">Ajouter une photo</a>

liste des photos de l'album ${albumname}: <br />

%for p in photos:
    ${p['filename']} <br />    
%endfor