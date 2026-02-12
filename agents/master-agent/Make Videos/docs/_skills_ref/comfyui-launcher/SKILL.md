# /comfyui-launcher
## Skill: ComfyUI Workflow Launcher

**Trigger:** `/comfyui-launcher [workflow] [song_id]`

**References:** RULES.md §3 Step 3, tech audit §5

**What it does:** Launches ComfyUI workflows for Phase 2+ AI video generation.

### Procedure
1. Verify ComfyUI is installed and running
2. Load workflow JSON from artist_profile.json `comfyui_workflow` field
3. Inject song-specific parameters (audio path, duration, genre prompts)
4. Submit to ComfyUI API
5. Monitor generation progress
6. Save output clips to catalog/{artist}/{song_id}/

### Supported Workflows
- Wan 2.1 T2V-1.3B (Mac compatible via GGUF)
- LTX-2 (audio-conditioned)
- Deforum (audio-reactive abstract)
- ToonCrafter (character interpolation)

### Phase Status
Phase 2+ — not required for baseline production.

### Related Skills
`/baseline-recipe-builder`, `/character-animator`
