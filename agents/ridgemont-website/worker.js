// Ridgemont Studio - Authenticated Music Streaming Worker
// This worker validates Firebase tokens and streams music from R2

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const filePath = url.searchParams.get('file');

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, DELETE, OPTIONS',
          'Access-Control-Allow-Headers': 'Authorization, Content-Type',
        }
      });
    }

    // If no file specified, return basic info
    if (!filePath) {
      return jsonResponse({
        service: 'Ridgemont Studio Music API',
        status: 'running'
      });
    }

    // PUBLIC ACCESS: tracks.json can be accessed without authentication
    // This allows the website to load the track list before user signs in
    if (filePath === 'tracks.json') {
      try {
        const object = await env.MUSIC_BUCKET.get('tracks.json');
        if (!object) {
          return jsonResponse({ error: 'Track list not found' }, 404);
        }

        const data = await object.text();
        return new Response(data, {
          headers: {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Cache-Control': 'public, max-age=60' // Cache for 1 minute
          }
        });
      } catch (error) {
        return jsonResponse({ error: 'Failed to load track list' }, 500);
      }
    }

    // AUTHENTICATED ACCESS: All music files require valid Firebase token
    const authHeader = request.headers.get('Authorization');
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return jsonResponse({ error: 'Unauthorized' }, 401);
    }

    const token = authHeader.slice(7);
    const isValid = await verifyFirebaseToken(token, env.FIREBASE_PROJECT_ID);

    if (!isValid) {
      return jsonResponse({ error: 'Invalid token' }, 401);
    }

    // Handle DELETE requests
    if (request.method === 'DELETE') {
      try {
        // Delete the file from R2
        await env.MUSIC_BUCKET.delete(filePath);

        // Update tracks.json to remove the deleted track
        const tracksObject = await env.MUSIC_BUCKET.get('tracks.json');
        if (tracksObject) {
          const tracksData = JSON.parse(await tracksObject.text());
          tracksData.tracks = tracksData.tracks.filter(t => t.file !== filePath);
          tracksData.lastUpdated = new Date().toISOString().split('T')[0];

          await env.MUSIC_BUCKET.put('tracks.json', JSON.stringify(tracksData, null, 2), {
            httpMetadata: { contentType: 'application/json' }
          });
        }

        return jsonResponse({ success: true, message: 'Track deleted' });
      } catch (error) {
        return jsonResponse({ error: error.message }, 500);
      }
    }

    // Stream file from R2 (GET request)
    try {
      const object = await env.MUSIC_BUCKET.get(filePath);

      if (!object) {
        return jsonResponse({ error: 'File not found' }, 404);
      }

      // Determine content type
      const contentType = getContentType(filePath);

      return new Response(object.body, {
        headers: {
          'Content-Type': contentType,
          'Access-Control-Allow-Origin': '*',
          'Cache-Control': 'private, max-age=3600'
        }
      });
    } catch (error) {
      return jsonResponse({ error: error.message }, 500);
    }
  }
};

// Verify Firebase ID token (basic validation)
async function verifyFirebaseToken(token, projectId) {
  try {
    // Decode the JWT (basic validation)
    const parts = token.split('.');
    if (parts.length !== 3) return false;

    const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));

    // Check expiration
    if (payload.exp < Date.now() / 1000) return false;

    // Check audience matches your project
    if (payload.aud !== projectId) return false;

    // Check issuer
    if (payload.iss !== `https://securetoken.google.com/${projectId}`) return false;

    return true;
  } catch {
    return false;
  }
}

// Get content type based on file extension
function getContentType(filePath) {
  const ext = filePath.split('.').pop().toLowerCase();
  const types = {
    'mp3': 'audio/mpeg',
    'wav': 'audio/wav',
    'flac': 'audio/flac',
    'aac': 'audio/aac',
    'm4a': 'audio/mp4',
    'ogg': 'audio/ogg',
    'json': 'application/json'
  };
  return types[ext] || 'application/octet-stream';
}

// JSON response helper
function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
    },
  });
}
