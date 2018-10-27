# Feelings with Ziggy
Feelings with Ziggy is an Alexa Skill built with Python. It was built for an Alexa Skills challenge, and is an educational game that aims to enhance the emotional literacy of young children by placing emotions to common experiences, ultimately helping children identify and express what they are feeling. This skill was built with AWS Lambda. Additionally it uses a s3 Bucket, Amazon EC2, and Amazon RDS (running an API I built with PHP and MySQL).

[View Demo](https://youtu.be/G2bXDq3MGb4)

## Prerequisites
*  [AWS Account](https://aws.amazon.com/getting-started/) - You will need to use [Lambda](https://aws.amazon.com/lambda/), [DynamoDB](https://aws.amazon.com/dynamodb/), and access to the [Alexa Skills Kit Developer Console](https://developer.amazon.com/alexa/console/ask)

## Installation

### AWS Lambda Setup
1. Go to the [AWS Console](https://console.aws.amazon.com/console/home) and click on the [Lambda](https://console.aws.amazon.com/lambda/home) link. Note: ensure you are in `us-east` or you won't be able to use Alexa with Lambda.
2. Click on the [Create a Lambda Function](https://console.aws.amazon.com/lambda/home?region=us-east-1#create) or `Get Started Now` button.
3. The first step is to `Author from scratch`.
4. Name the Lambda Function with a name significant to the skill.
5. Select the runtime as `Python`.
6. Select an execution role as `lambda_basic_execution`.
7. Click on the `Create Function` button to move on. 
8. Scroll down to the Function Code section and you will see a code editor.
9. Clone the project. 
```
git clone git@github.com:smithsa/feelings-with-ziggy.git
```

10. Copy and pass the contents of `lambda_function.py` into the code editor.
11. Save the code by clicking the `Save` button on the right hand corner of the screen.
12. Set the Event Source type as `Alexa Skills Kit` and Enable it now. Click `Submit`.
13. Copy the ARN from the top right to be used later in the Alexa Skill Setup. It will look something similar to `arn:aws:lambda:us-east-1:100000012345:function:your-skill-name`.

### Alexa Skill Setup
1. Go to the [Alexa Console](https://developer.amazon.com/edw/home.html) and click `Get Started` under Alexa Skills Kit and then click the `Add a New Skill` button in the top right.
2. Set the `name` of the new skill name and the language.
3. Select Custom Skill as the model.
4. Proceed by clicking on the `Next` Button.
5. Click the `Invocation` tab and give the skill an appropriate `invocation name` - this is what is used to activate your skill.
6. On the left click the `JSON Editor` tab, then add the contents of models.json to text editor on that page.
7. Click the `Endpoint` tab and set the AWS Lambda ARN. Set the default as the string you copied in the previous section that looks like this: `arn:aws:lambda:us-east-1:100000012345:function:your-skill-name`.
8. Build the model and you are now ready to test the skill.


## Usage

You can test and run the skill through the command line or the Alexa Skills Kit Developer Console.

**Command Line**

Run the command below. For more information on this command refer to Alexa's [Simulate Command Documentaiton](https://developer.amazon.com/docs/smapi/ask-cli-command-reference.html#simulate-command)
```
ask simulate -t [insert command here]
```

**Alexa Skills Kit Developer Console**

You can navigate to the [Alexa Skills Kit Developer Console](https://developer.amazon.com/alexa/console/ask). Select the skill you are workig on, and select the "Test" tab menu item at the top of the page. You can open the skill by typing "open [your skill name]." You can enter any other commands as well.

Refer to Amazon's [Alexa Skills Kit Developer Console: Test](https://www.youtube.com/watch?v=lYImJ2H__BY) video from more instruction on how to test withing the console.

To understand the commands you can give the skill watch the [view demo](https://youtu.be/G2bXDq3MGb4).

## Built With
*  [ASK SDK Python](https://github.com/alexa/alexa-skills-kit-sdk-for-python)
*  [Python](https://www.python.org/)
*  [AWS Lambda](https://aws.amazon.com/lambda/)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

MIT © [Sade Smith](https://sadesmith.com)

