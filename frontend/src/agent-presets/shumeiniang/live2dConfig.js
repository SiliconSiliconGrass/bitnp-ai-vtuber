import testExp from './faceParamExpressions/test.faceexp.js';
import nod from './faceParamExpressions/nod.faceexp.js';
import shakeHead from './faceParamExpressions/shake_head.faceexp.js';
import wink from './faceParamExpressions/wink.faceexp.js';

export default {
    modelURL: '/Resources/DAver3.0/DAnew_version.model3.json', canvas: null,
    motionDict: {
        // '流汗': { group: 'basic', order: 0, duration: 1000 },
        // '摇头': { group: 'basic', order: 1, duration: 2000 },
        // '招手': { group: 'basic', order: 2, duration: 1000 },
        // '指': { group: 'basic', order: 3, duration: 1000 }
    },
    expressionDict: {},
    faceParamExpressionDict: {
        '点头': {
            data: nod,
            duration: 1000
        },

        '摇头': {
            data: shakeHead,
            duration: 1000
        },

        'wink': {
            data: wink,
            duration: 1000
        },

    },
}