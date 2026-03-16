#!/usr/bin/env node
import * as qcdn from '@q/qcdn';
import path from 'path';
import fs from 'fs';
import { fileURLToPath } from 'url';

// 确保能正确处理 ESM 下的 __dirname 等
// const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function main() {
    const args = process.argv.slice(2);

    if (args.length === 0) {
        console.error('请提供要上传的文件路径。用法: node upload.js <file1> [file2...]');
        process.exit(1);
    }

    // 处理文件路径
    const filePaths = args.map(arg => path.resolve(process.cwd(), arg));

    // 验证文件存在
    const existingFiles = filePaths.filter(p => {
        if (!fs.existsSync(p)) {
            console.warn(`警告: 文件不存在，已跳过: ${p}`);
            return false;
        }
        return true;
    });

    if (existingFiles.length === 0) {
        console.error('错误: 没有有效的待上传文件。');
        process.exit(1);
    }

    // 配置选项
    const opts = {
        https: true,
        keepName: false,
        min: true, // 开启压缩
        force: true // 忽略错误
    };

    try {
        // qcdn.upload 支持数组，返回 Promise
        const result = await qcdn.upload(existingFiles, opts);

        // 输出 JSON 结果供调用方解析
        console.log(JSON.stringify(result, null, 2));
    } catch (err) {
        console.error('上传失败:', err);
        process.exit(1);
    }
}

main();
