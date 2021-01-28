docker run --name static_consent -p 8083:80 -v $(pwd)/consent_form:/usr/share/nginx/html:ro -d nginx
echo running on http://localhost:8083
