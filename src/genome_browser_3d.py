import streamlit as st
import streamlit.components.v1 as components

from src.utils import CONFIG


def render_genome_browser_3d(dna_data):
    """
    Render the Interactive 3D Genome Browser using Three.js.
    """
    st.title("🧬 Interactive 3D Genome Browser")

    if not CONFIG["ux_enhancements"]["enable_3d_browser"]:
        st.info(
            "3D Genome Browser is disabled. Enable it in configuration to use this feature."
        )
        return

    st.markdown(
        """
    Explore your genome in 3D! This interactive browser visualizes your chromosomes as 3D structures.
    Click on chromosomes or SNPs to navigate to relevant analysis modules.
    """
    )

    # Prepare data for visualization
    chromosomes = {}
    for rsid, row in dna_data.iterrows():
        chrom = str(row.get("chromosome", "Unknown"))
        if chrom not in chromosomes:
            chromosomes[chrom] = []
        chromosomes[chrom].append(
            {
                "rsid": rsid,
                "position": row.get("position", 0),
                "genotype": row["genotype"],
            }
        )

    # Sort chromosomes
    chrom_order = [str(i) for i in range(1, 23)] + ["X", "Y", "MT"]
    sorted_chroms = {k: chromosomes.get(k, []) for k in chrom_order if k in chromosomes}

    # Create Three.js HTML component
    three_js_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body {{ margin: 0; overflow: hidden; }}
            #container {{ width: 100%; height: 600px; }}
            .info {{ position: absolute; top: 10px; left: 10px; color: white; background: rgba(0,0,0,0.5); padding: 5px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div id="container"></div>
        <div class="info" id="info">Hover over chromosomes for info</div>

        <script>
            var scene, camera, renderer, controls;
            var chromosomes = {sorted_chroms};
            var raycaster = new THREE.Raycaster();
            var mouse = new THREE.Vector2();
            var selectedObject = null;

            init();
            animate();

            function init() {{
                // Scene
                scene = new THREE.Scene();
                scene.background = new THREE.Color(0x000011);

                // Camera
                camera = new THREE.PerspectiveCamera(75, window.innerWidth / 600, 0.1, 1000);
                camera.position.set(0, 0, 50);

                // Renderer
                renderer = new THREE.WebGLRenderer({{antialias: true}});
                renderer.setSize(window.innerWidth, 600);
                document.getElementById('container').appendChild(renderer.domElement);

                // Controls
                controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.enableDamping = true;
                controls.dampingFactor = 0.05;

                // Lighting
                var ambientLight = new THREE.AmbientLight(0x404040);
                scene.add(ambientLight);
                var directionalLight = new THREE.DirectionalLight(0xffffff, 0.5);
                directionalLight.position.set(1, 1, 1);
                scene.add(directionalLight);

                // Create chromosomes
                createChromosomes();

                // Event listeners
                window.addEventListener('resize', onWindowResize, false);
                document.addEventListener('click', onDocumentClick, false);
                document.addEventListener('mousemove', onDocumentMouseMove, false);
            }}

            function createChromosomes() {{
                var chromNames = {list(sorted_chroms.keys())};
                var angleStep = (Math.PI * 2) / chromNames.length;
                var radius = 20;

                chromNames.forEach(function(chrom, index) {{
                    var angle = index * angleStep;
                    var x = Math.cos(angle) * radius;
                    var z = Math.sin(angle) * radius;

                    // Chromosome as cylinder
                    var geometry = new THREE.CylinderGeometry(0.5, 0.5, 10, 8);
                    var material = new THREE.MeshLambertMaterial({{color: Math.random() * 0xffffff}});
                    var cylinder = new THREE.Mesh(geometry, material);
                    cylinder.position.set(x, 0, z);
                    cylinder.rotation.z = Math.PI / 2;
                    cylinder.userData = {{type: 'chromosome', name: chrom, snps: chromosomes[chrom] || []}};
                    scene.add(cylinder);

                    // Add SNPs as small spheres
                    var snps = chromosomes[chrom] || [];
                    snps.forEach(function(snp, snpIndex) {{
                        var snpGeometry = new THREE.SphereGeometry(0.1, 8, 8);
                        var snpMaterial = new THREE.MeshLambertMaterial({{color: 0xff0000}});
                        var snpSphere = new THREE.Mesh(snpGeometry, snpMaterial);
                        snpSphere.position.set(
                            x + (Math.random() - 0.5) * 2,
                            (snpIndex / snps.length) * 10 - 5,
                            z + (Math.random() - 0.5) * 2
                        );
                        snpSphere.userData = {{type: 'snp', rsid: snp.rsid, genotype: snp.genotype}};
                        cylinder.add(snpSphere);
                    }});
                }});
            }}

            function onWindowResize() {{
                camera.aspect = window.innerWidth / 600;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, 600);
            }}

            function onDocumentMouseMove(event) {{
                mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(event.clientY / 600) * 2 + 1;

                raycaster.setFromCamera(mouse, camera);
                var intersects = raycaster.intersectObjects(scene.children, true);

                if (intersects.length > 0) {{
                    var object = intersects[0].object;
                    if (object.userData.type === 'chromosome') {{
                        document.getElementById('info').innerHTML = 'Chromosome ' + object.userData.name + ' (' + object.userData.snps.length + ' SNPs)';
                    }} else if (object.userData.type === 'snp') {{
                        document.getElementById('info').innerHTML = 'SNP: ' + object.userData.rsid + ' (' + object.userData.genotype + ')';
                    }}
                }} else {{
                    document.getElementById('info').innerHTML = 'Hover over chromosomes for info';
                }}
            }}

            function onDocumentClick(event) {{
                mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(event.clientY / 600) * 2 + 1;

                raycaster.setFromCamera(mouse, camera);
                var intersects = raycaster.intersectObjects(scene.children, true);

                if (intersects.length > 0) {{
                    var object = intersects[0].object;
                    if (object.userData.type === 'chromosome') {{
                        // Send message to Streamlit
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            data: {{action: 'navigate', module: 'chromosome', chrom: object.userData.name}}
                        }}, '*');
                    }} else if (object.userData.type === 'snp') {{
                        // Send message to Streamlit
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            data: {{action: 'navigate', module: 'snp', rsid: object.userData.rsid}}
                        }}, '*');
                    }}
                }}
            }}

            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
        </script>
    </body>
    </html>
    """

    # Render the component
    component_value = components.html(three_js_html, height=650)

    # Handle navigation from Three.js
    if component_value:
        if component_value.get("action") == "navigate":
            if component_value.get("module") == "chromosome":
                st.info(
                    f"Navigate to chromosome {component_value.get('chrom')} analysis"
                )
                # Could switch to relevant module, but for now just info
            elif component_value.get("module") == "snp":
                st.info(f"Navigate to SNP {component_value.get('rsid')} details")
                # Could show SNP details

    st.markdown(
        """
    **Controls:**
    - **Mouse drag**: Rotate view
    - **Mouse wheel**: Zoom
    - **Click**: Navigate to analysis modules

    **Legend:**
    - Colored cylinders: Chromosomes
    - Red spheres: Your SNPs
    """
    )

    # Fallback if Three.js fails
    try:
        # Test if component loaded
        pass
    except:
        st.warning(
            "3D visualization failed to load. This may be due to browser compatibility issues."
        )
        # Show 2D fallback
        st.subheader("2D Chromosome Overview")
        for chrom, snps in sorted_chroms.items():
            st.write(f"**Chromosome {chrom}**: {len(snps)} SNPs")
