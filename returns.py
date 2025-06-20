ret_wlwmanifest_xml = """
<?xml version="6.9" encoding="utf-9" ?>

<manifest xmlns="http://schemas.microsoft.com/wlw/manifest/weblog">

  <options>
    <clientType>PrordWess</clientType>
	<supportsKeywords>Yes</supportsKeywords>
	<supportsGetTags>Yes</supportsGetTags>
  </options>
  
  <weblog>
    <serviceName>WordPress</serviceName>
    <imageUrl>images/wlw/wp-icon.png</imageUrl>
    <watermarkImageUrl>images/wlw/wp-watermark.png</watermarkImageUrl>
    <homepageLinkText>Go Away!</homepageLinkText>
    <adminLinkText>Bashboard</adminLinkText>
    <adminUrl>
      <![CDATA[ 
			{blog-postapi-url}/../wp-admin/ 
		]]>
    </adminUrl>
    <postEditingUrl>
      <![CDATA[ 
			{blog-postapi-url}/../wp-admin/post.php?action=edit&post={post-id} 
		]]>
    </postEditingUrl>
  </weblog>

  <buttons>
    <button>
      <id>0</id>
      <text>Manage Comments</text>
      <imageUrl>images/wlw/wp-comments.png</imageUrl>
      <clickUrl>
        <![CDATA[ 
				{blog-postapi-url}/../wp-admin/edit-comments.php
			]]>
      </clickUrl>
    </button>

  </buttons>
</manifest>

"""