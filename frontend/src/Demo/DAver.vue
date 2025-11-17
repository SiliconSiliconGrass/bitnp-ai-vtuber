<template>
    <div>
        <div class="background-image"></div>
        <div class="danmuku-area" ref="danmukuArea"></div>
        <div class="user-interface" id="user-interface">
            <!-- UI区域 -->
            <button v-if="!audioEnabled" @click="enableAudioActivities">启用音频</button>
            <!-- <input ref="input_area" type="text" v-model="inputText" placeholder="请输入...">
            <button @click="switchMicrophoneMode">{{ (microphoneOn) ? '闭麦' : '开麦' }}</button> -->
        </div>

        <div class="logo-background"></div>

        <div ref="configUI" :class="showConfigUI ? 'config-ui' : 'config-ui config-ui-hidden'">
            <!--  -->
            <h1 class="config-title">设置菜单</h1>
            <span>按“=”键随时唤出此菜单</span>
            <br>
            <br>

            <label>
                <input type="checkbox" v-model="enableDictation">
                启用听写
            </label><br>

            <label>
                <input type="checkbox" v-model="enableFullScreen">
                全屏模式
            </label><br>

            <label>
                <input type="checkbox" v-model="allowPauseDictation">
                在 AI 说话时禁用语音识别
            </label><br>
            
        </div>

        <div class="subtitle-area">
            <div ref="subtitleContainer1" class="subtitle-container subtitle-container-hidden">
                <div ref="subtitleInnerContainer1" class="subtitle-inner-container">
                    <span ref="subtitle1" class="subtitle"></span>
                </div>
            </div>
        </div>

        <!-- <iframe 
            ref="faceCapIframe"
            src="http://localhost:9235/"
            class="iframe"
            allowtransparency="true"
            @load="onIframeLoad"
        ></iframe> -->

        <!-- 摄像头图像显示 -->
        <!-- <div class="camera-container">
            <img class="camera-image" :src="imageSrc" />
        </div> -->

        <!-- 听写结果显示 -->
        <div class="subtitle-area stt">
            <div ref="subtitleContainerStt" class="subtitle-container stt subtitle-container-hidden">
                <div ref="subtitleInnerContainerStt" class="subtitle-inner-container">
                    <span ref="subtitleStt" class="subtitle"></span>
                </div>
            </div>
        </div>

        <div class="canvas-container">
            <canvas ref="testCanvas1" id="leftCanvas" class="left-canvas"></canvas>
            <canvas ref="testCanvas2" id="rightCanvas" class="right-canvas"></canvas>
        </div>

        <div v-if="debug" class="visualize-area">
            <!-- 数据可视化区域 -->
            <div v-if="actionQueueWatcher" class="action-queue">
                <div v-for="(action, i) in actionQueueWatcher" :key="i" class="action-container">
                    <span> 动作类型: {{ action.type }} <br>
                        内容: {{ action.data }}
                    </span>
                </div>
            </div>

            <div v-if="resourcesWatcher" class="resource-bank">
                <!-- {{ resourceManager.resourceBank }} <br>
                {{ resourceManager.resourceIds }} -->
                <div v-for="(resource, i) in resourcesWatcher" :key="i" class="resource-container">
                    <!-- {{ resourceManager.get(id) }} -->
                    <span> 资源类型: {{ resource.type }} <br>
                        是否就绪: {{ resource.ready }} <br>
                        内容: {{ resource.data }}
                    </span>
                </div>
            </div>
        </div>

        <div hidden>
            <!-- 与live2d模块通信 -->
            <div id="lipSyncVal">{{ (this.$refs.mao_audio_bank) ? this.$refs.mao_audio_bank.volume : 0 }}</div>
            <div id="l2dEventTrigger"></div>
            <div id="l2dCallbackTrigger"></div>
            <div id="l2dResourcesPath">{{ l2dResourcesPath }}</div>
            <div id="l2dModelDirPath">{{ l2dModelDirPath }}</div>
        </div>
    </div>
</template>

<script>
import { ShuMeiNiang } from '@/agent-presets/shumeiniang/shumeiniang';

export default {
    components: {
        // ... 
    },
    data() {
        return {
            microphoneOn: false,
            debug: false,
            audioEnabled: false, // The user needs to interact with the page (by clicking the button) to enable audio

            imageSrc: "",

            // app vars
            showConfigUI: false,
            enableDictation: false,
            enableFullScreen: false,
            allowPauseDictation: true,
        };
    },

    watch: {
        enableFullScreen(newVal) {
            if (newVal) {
                this.enterFullscreen();
            } else {
                this.exitFullscreen();
            }
        }
    },

    methods: {
        enterFullscreen() {
            const element = document.documentElement; // 整个页面全屏
            const requestMethod =
                element.requestFullscreen ||
                element.webkitRequestFullscreen ||
                element.mozRequestFullScreen ||
                element.msRequestFullscreen;

            if (requestMethod) {
                requestMethod.call(element).catch((err) => {
                    console.error("全屏失败:", err);
                    this.enableFullScreen = false; // 失败时重置状态
                });
            }
        },

        exitFullscreen() {
            const exitMethod =
                document.exitFullscreen ||
                document.webkitExitFullscreen ||
                document.mozCancelFullScreen ||
                document.msExitFullscreen;

            if (exitMethod) {
                exitMethod.call(document);
            }
        },

        enableAudioActivities() {
            this.agent1.resourceManager.audioBank.handleUserGesture();
            // this.agent2.resourceManager.audioBank.handleUserGesture();
            this.audioEnabled = true;
        },

        // interrupt() {
        //     this.actionQueue.queue = [];
        //     this.resourceManager.clearResources();

        //     clearTimeout(this.resourceManager.timeoutId);
        //     this.resourceManager.mainLoop();
        //     clearTimeout(this.actionQueue.timeoutId);
        //     this.actionQueue.mainLoop();
        //     this.actionQueue.dispatchEvent(new Event('empty'));

        //     for (let key in this.agent.subtitles) {
        //         let subtitle = this.agent.subtitles[key];
        //         if (subtitle) {
        //             subtitle.clear();
        //         }
        //     }
        // },

        async recordChat(message) {
            /**
             * 将用户输入记录在userInputBuffer中
             * @param message String
             */
            // this.userInputBuffer.push(message);
            this.agent1.userInputBuffer.push(message);
            console.log(`Add text: ${message}`);
        },

        /**
         * 暂停听写功能，向语音识别后端的 /message 接口发送 POST 请求
         * 将 enableDictation 参数设为 false
         */
        async pauseDictation() {
            try {
                const response = await fetch('http://localhost:9236/message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ enableDictation: false }),
                });

                if (!response.ok) {
                    throw new Error(`请求失败，状态码: ${response.status}`);
                }
            } catch (error) {
                console.error('暂停听写请求出错:', error);
            }
        },

        /**
         * 继续/启用听写功能，向语音识别后端的 /message 接口发送 POST 请求
         * 将 enableDictation 参数设为 true
         */
        async resumeDictation() {
            try {
                const response = await fetch('http://localhost:9236/message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ enableDictation: true }),
                });

                if (!response.ok) {
                    throw new Error(`请求失败，状态码: ${response.status}`);
                }
            } catch (error) {
                console.error('暂停听写请求出错:', error);
            }
        },

    },

    mounted() {
        const self = this;

        // 0. Agent Setup
        const agent1 = ShuMeiNiang(this.$refs.testCanvas1, this.$refs.subtitle1, null, this.$refs.danmukuArea);
        agent1.mainLoop(agent1); // 启动AI树莓娘
        this.agent1 = agent1;

        console.log("agent", agent1); // debug

        // 1. STT Management
        // 1.1 stt monitor vars        
        let sttTime = -1;
        let responseEndTime = Date.now();
        let sttText = "";
        let inResponse = false;
        let prevEnableDictation = this.enableDictation;
        const STT_BACKEND_PORT = 9236;

        // 1.2 stt subtitle display
        let displayIntervalId = null;
        const subtitleSttEle = this.$refs.subtitleStt;
        function displaySttText(text) {
            clearInterval(displayIntervalId);

            text = "(语音识别) " + text;
            displayIntervalId = setInterval(() => {
                let currLength = subtitleSttEle.innerHTML.length
                if (currLength >= text.length) {
                    let currContent = subtitleSttEle.innerHTML;
                    setTimeout(() => {
                        if (subtitleSttEle.innerHTML === currContent) {
                            subtitleSttEle.innerHTML = "";
                        }
                    }, 5000)
                    clearInterval(displayIntervalId);
                    return;
                }
                subtitleSttEle.innerHTML += text[currLength];
            }, 50);
        }

        // 1.3 stt input loop
        const sttLoopId = setInterval(() => {
            fetch(`http://localhost:${STT_BACKEND_PORT}/get_dictation`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                // console.log('获取到的听写数据:', data); // debug
                // 可根据需求添加处理获取到的JSON数据的逻辑
                const dictationTime = data.time * 1000;

                if (!prevEnableDictation && this.enableDictation) {
                    responseEndTime = Date.now();
                }

                if (!inResponse && this.enableDictation && dictationTime > sttTime && dictationTime - responseEndTime >= 1000) {
                // if ((!inResponse || !this.allowPauseDictation) && this.enableDictation && dictationTime > sttTime) {
                    // sttTime = data.time;
                    sttTime = dictationTime;
                    sttText = data.dictation;
                    
                    // commit stt text
                    this.recordChat(sttText);
                    displaySttText(sttText);

                    console.log("Add stt text:", sttText); // debug
                }
                prevEnableDictation = this.enableDictation;
            })
            .catch(error => {
                console.error('Error occurred when getting dictation data:', error);
            });
        }, 100);

        // 1.4 stt message sender loop
        const sttMessageSenderLoopId = setInterval(() => {
            if ((self.enableDictation && !inResponse) || (!self.allowPauseDictation)) {
                self.resumeDictation();
            } else {
                self.pauseDictation();
            }
        }, 1000);

        // 2. Agent Event Handlers
        // 2.1 handle start of response
        agent1.addEventListener('start_of_response', (e) => {
            inResponse = true;
            self.pauseDictation(); // 在AI说话期间禁用语音识别
        });

        // 2.2 handle end of response
        agent1.addEventListener('end_of_response', (e) => {
            inResponse = false;
            const response = e.detail.response;
            const now = Date.now();
            responseEndTime = now;

            if (self.enableDictation) {
                self.resumeDictation();
            }
        });

        // 3. show config ui by keyboard
        document.addEventListener("keydown", (e) => {
            if (e.key === '=') {
                this.showConfigUI = !this.showConfigUI;
            }
        });

        // 4. Subtitle Container Animations
        // 4.1 agent subtitle container monitor
        const subtitleMonitorId = setInterval(() => {
            if (this.$refs.subtitle1.innerHTML !== "") {
                this.$refs.subtitleContainer1.className = "subtitle-container"
            } else {
                this.$refs.subtitleContainer1.className = "subtitle-container subtitle-container-hidden"
            }
            this.$refs.subtitleInnerContainer1.scrollTo({
                top: this.$refs.subtitleInnerContainer1.scrollHeight,
                behavior: 'smooth' // 平滑滚动
            });
        }, 100);

        // 4.2 subtitle stt container monitor
        const subtitleSttMonitorId = setInterval(() => {
            if (this.$refs.subtitleStt.innerHTML !== "") {
                this.$refs.subtitleContainerStt.className = "subtitle-container stt"
            } else {
                this.$refs.subtitleContainerStt.className = "subtitle-container stt subtitle-container-hidden"
            }
            this.$refs.subtitleInnerContainerStt.scrollTo({
                top: this.$refs.subtitleInnerContainerStt.scrollHeight,
                behavior: 'smooth' // 平滑滚动
            });
        }, 100);

        // 5. Face Capture
        // 5.1 fetch camera image
        async function fetchImage() {
            try {
                const response = await fetch('http://localhost:9234/get_face_image')
                const data = await response.json()
                self.imageSrc = `data:image/png;base64,${data.faceImage}` // 关键：添加 Data URL 前缀
            } catch (error) {
                console.error('获取图片失败:', error)
            }
        }
        setTimeout(() => {
            const fetchImageLoopId = setInterval(() => {
                fetchImage()
            }, 30);
        }, 1000);

        // this.recordChat('[系统提示：外场活动开始了，给大家打个招呼吧，并且招揽同学们加入网协！！！]'); // 开头
    },
};
</script>

<style>
#app {
    position: absolute;
    left: 0;
    top: 0;
    width: 100vw;
    height: 100vh;
    font-family: Avenir, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-align: center;
    color: #2c3e50;
}

.danmuku-area {
    position: fixed;
    width: 30vw;
    height: 100vh;
    /* border: 1px solid black; */
    overflow-y: scroll;
}
.danmuku-area::-webkit-scrollbar {
    display: none;
}

.canvas-container {
    box-sizing: content-box;
    position: fixed;
    margin: 0;
    padding: 0;
    /* display: flex; */
    /* 使用flex布局 */
    width: 100%;
    /* 充满屏幕宽度 */
    height: 100vh;
    /* 充满屏幕高度 */
}

.left-section,
.right-section {
    flex: 1;
    /* 均等分配空间 */
    height: 100%;
    /* 继承容器高度 */
    position: relative;
}

.left-canvas {
    position: fixed;
    margin: 0;
    padding: 0;
    width: 100vw; /* modified */
    height: 100vh;
    left: 0;
    top: 0;
}


.right-canvas {
    position: fixed;
    margin: 0;
    padding: 0;
    width: 50vw;
    height: 100vh;
    right: 0;
    top: 0;
}

.canvas {
    position: absolute;
    margin: 0;
    padding: 0;
    display: block;
    /* 避免canvas默认inline带来的空白间隙 */
    width: 100%;
    /* 充满父容器 */
    height: 100%;
    /* 充满父容器 */

    opacity: 1;
    transform: translateX(0);
    transition: opacity 0.5s ease, transform 0.5s ease;
}

.canvas_hidden {
    transform: translateX(-50px);
    opacity: 0;
}



.user-interface {
    z-index: 999;
    position: fixed;
    width: 90vw;
    /* 1vw = 视口宽的的1% */
    max-width: 600px;
    left: 50vw;
    top: 100vh;
    transform: translate(-50%, -150%);
    /* border: 1px solid black; */
    /* background-color: yellow; */
    /* -webkit-app-region: drag; */
}

.user-interface>* {
    border-radius: 10px;
    margin: 10px;
    font-family: Avenir, Helvetica, Arial, sans-serif;
    font-size: 2em;
}

.user-interface>input {
    width: 80%;
    max-width: 800px;
}

.subtitle-area {
    position: fixed;
    z-index: 998;
    margin: 0;
    left: 0;
    padding: 0;
    width: 50vw;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: last baseline;

    perspective: 1000px; /* 3D 透视焦距 */
}

@keyframes subtitle-hover {
    0% { transform: rotateY(20deg) rotateX(-20deg) translate(100px, -300px);}
    25% { transform: rotateY(25deg) rotateX(-15deg) translate(100px, -280px);}
    50% { transform: rotateY(20deg) rotateX(-20deg) translate(100px, -300px);}
    75% { transform: rotateY(15deg) rotateX(-25deg) translate(100px, -320px);}
    100% { transform: rotateY(20deg) rotateX(-20deg) translate(100px, -300px);}
}

@keyframes subtitle-hide {
    0% { transform: rotateY(20deg) rotateX(-20deg) translate(100px, -300px);}
    100% { transform: rotateY(0deg) rotateX(90deg) translate(0, 0);}
}

.subtitle-container {
    margin-left: 10%;
    width: 80%;
    margin-right: 10%;

    padding-top: 20px;
    padding-bottom: 30px;
    padding-left: 40px;
    padding-right: 40px;

    text-align: left;

    aspect-ratio: 907/200;
    background-image: url("@/assets/tooltip.png");
    background-size: 100% 100%;
    background-repeat: no-repeat;

    opacity: 1;
    z-index: 1000;
    transform-style: preserve-3d;
    transform: rotateY(20deg) rotateX(-20deg) translate(100px, -300px);
    animation: subtitle-hover 10s infinite linear 0.5s;
    transition: opacity 0.5s ease, transform 0.5s ease;
}

.subtitle-container-hidden {
    opacity: 0;
    transform: rotateY(20deg) rotateX(90deg) translate(0, 0);
    transition: opacity 0.5s ease, transform 0.5s ease;
    animation: subtitle-hide 0.5s ease-out;
}

.subtitle-inner-container {
    width: 100%;
    height: 100%;
    overflow-y: scroll;
}
.subtitle-inner-container::-webkit-scrollbar {
  display: none; /* 完全隐藏滚动条 */
}

.subtitle {
    font-size: 2em;
    font-weight: 1000;
    -webkit-text-stroke: 1px rgb(255, 255, 255);
    text-shadow: 2px 2px rgb(43, 38, 43);
    user-select: none;
    color: rgb(56, 225, 255);
}

/* stt subtitle container */

@keyframes subtitle-hover-stt {
    0% { transform: rotateY(-20deg) rotateX(-20deg) translate(-100px, 0);}
    25% { transform: rotateY(-25deg) rotateX(-15deg) translate(-100px, 0);}
    50% { transform: rotateY(-20deg) rotateX(-20deg) translate(-100px, 0);}
    75% { transform: rotateY(-15deg) rotateX(-25deg) translate(-100px, 0);}
    100% { transform: rotateY(-20deg) rotateX(-20deg) translate(-100px, 0);}
}

@keyframes subtitle-hide-stt {
    0% { transform: rotateY(-20deg) rotateX(-20deg) translate(100px, 0);}
    100% { transform: rotateY(0deg) rotateX(90deg) translate(0, 0);}
}

.subtitle-area.stt {
    position: fixed;
    margin: 0;
    left: 50vw;
    padding-top: 10vh;
    width: 50vw;
    height: 100vh;

    align-items: first baseline;
}
.subtitle-container.stt {
    transform: rotateY(-20deg) rotateX(-20deg) translate(-100px, 0);
    animation: none;
    transition: opacity 0.5s ease, transform 0.5s ease;
    animation: subtitle-hover-stt 10s infinite linear 0.5s;
}

.subtitle-container-hidden.stt {
    transform: rotateY(-20deg) rotateX(90deg) translate(0, 0);
    animation: subtitle-hide-stt 0.5s ease-out;
}

.visualize-area {
    position: absolute;
    z-index: 2;
    right: 5%;
    width: 20vw;
}

.action-queue {
    position: relative;
    width: 100%;
}

.action-container {
    position: relative;
    margin: 5px;
    width: 100%;
    border: 1px solid black;
    background: rgb(116, 116, 238);
    border-radius: 10px;
    color: white;
}

.resource-bank {
    position: relative;
    width: 100%;
}

.resource-container {
    position: relative;
    margin: 5px;
    width: 100%;
    border: 1px solid black;
    background: rgb(238, 116, 179);
    border-radius: 10px;
    color: white;
}

.background-image {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    /* background-image: url('@/assets/bg01020.png'); */
    background: linear-gradient(to top, rgb(4, 4, 38), rgb(44, 26, 90));
    background-position: center;
    background-repeat: no-repeat;
    background-size: cover;
    z-index: -1
}

.iframe {
    position: fixed;
    border: none;
    background-color: transparent;
    z-index: 998;
    top: 0;
    right: 0;
    width: 50vw;
    height: 100vh;
}

.config-ui {
    border: #2c3e50;
    background-color: rgb(28, 0, 57);
    border-radius: 10px;
    padding: 10px;
    color: white;
    position: fixed;
    top: 25vh;
    left: 25vw;
    width: 50vw;
    height: 50vh;
    opacity: 1;
    z-index: 9999;
    transform: translate(0, 0);
    transition: opacity 0.5s ease, transform 0.5s ease;
}

.config-ui-hidden {
    opacity: 0;
    transform: translate(0, 1000px);
}

.camera-container {
    z-index: 5;
    position: fixed;
    right: 0vw;
    width: 25vw;
}

.camera-image {
    width: 100%;
    height: 100%;
    border-radius: 10px;
}

.logo-background {
    position: fixed;
    width: 30vw;
    left: 35vw;
    top: 20vh;
    aspect-ratio: 647/493;

    background-image: url("@/assets/logo_background.png");
    background-size: 100% 100%;
    background-repeat: no-repeat;
}
</style>